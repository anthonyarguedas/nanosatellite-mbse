#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Bounded adapter smoke: one exact gate and one long-abstract Record Details."""
from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path

import run as final

# Capture public bibliographic cells only. Never save OATD detail route URLs.
DETAIL_AUDIT = r"""() => {
  const table = document.querySelector('table.recordTable');
  const labels = table ? Array.from(table.rows).map(r => r.cells[0]?.textContent.trim()) : [];
  const row = table ? Array.from(table.rows).find(r => r.cells[0]?.textContent.trim() === 'Abstract') : null;
  const cell = row?.cells[1];
  return {
    labels,
    abstract_cell_text: cell?.textContent ?? null,
    abstract_cell_visible_text: cell?.innerText ?? null,
    abstract_cell_markup: cell?.innerHTML ?? null,
    type_degree_fields: table ? Array.from(table.rows).filter(r =>
      /^(Type|Document Type|Publication Type|Degree|Degree Name|Degree Level|Level|Language|Issued Date)$/.test(r.cells[0]?.textContent.trim())
    ).map(r => ({label: r.cells[0].textContent.trim(), value: r.cells[1]?.textContent.trim()})) : []
  };
}"""


async def smoke(root: Path):
    root.mkdir(parents=True, exist_ok=False)
    adapter = final.load_adapter()
    queries = final.load_queries()
    event = final.plan_event(adapter, 'G1-MH', queries.GATE_QUERIES['G1-MH'])
    event['timeout_seconds'] = 180.0
    final.write_exclusive_json(root / 'plan.json', {
        'created_at_utc': final.now(), 'merge_eligible': False,
        'source_search_requests': 1, 'detail_requests': 1,
        'purpose': 'Verify the exact gate and full abstract extraction against public detail DOM',
        'selected_detail_id': 'handle:1721.1/98586',
        'event': event, 'script_sha256': final.digest(Path(__file__)),
        'adapter_sha256': final.digest(final.ADAPTER_PATH),
    })
    receipt = {'started_at_utc': final.now(), 'merge_eligible': False}
    from playwright.async_api import async_playwright
    async with async_playwright() as pw, adapter._LeaseCleanup() as cleanup:
        lease = await adapter.open_owned_chrome_page(
            pw, cdp_url='http://127.0.0.1:9222', headless=False,
            timeout_seconds=180.0, chrome_executable=None)
        cleanup.lease = lease
        page = lease.page
        try:
            snapshot, config, payloads, retries = await final.capture_snapshot(
                adapter, page, event, output=root / 'gate.json')
            for kind, payload in payloads.items():
                final.write_exclusive_bytes(root / payload.evidence['file_name'], payload.data)
            final.write_exclusive_json(root / 'gate.json', {
                'merge_eligible': False, 'query': event['effective_query'],
                'snapshot': final.snapshot_payload(adapter, snapshot),
                'screenshots': {k: p.evidence for k, p in payloads.items()},
            })
            print(json.dumps({'gate': 'G1-MH', 'total': snapshot.total}), flush=True)
            card = next(c for c in snapshot.cards if c.record_id == 'handle:1721.1/98586')
            await asyncio.sleep(60)
            record = await adapter.read_shared_population_detail(
                page, card=card, configuration=config, timeout_seconds=180.0,
                busy_retry_budget=adapter.OATDBusyRetryBudget(max_retries=0, initial_delay_seconds=120.0))
            audit = await page.evaluate(DETAIL_AUDIT)
            final.write_exclusive_json(root / 'detail-audit.json', {
                'merge_eligible': False, 'record': record, 'dom': audit,
            })
            await page.screenshot(path=str(root / 'detail.png'), full_page=True)
            receipt['status'] = 'complete'
            print(json.dumps({'abstract_characters': len(record['abstract']),
                              'abstract_ends': record['abstract'][-200:],
                              'cell_text_characters': len(audit['abstract_cell_text'] or ''),
                              'type_degree_fields': audit['type_degree_fields']}), flush=True)
        except Exception as error:
            receipt['status'] = 'failed'
            receipt['error_type'] = type(error).__name__
            receipt['error'] = str(error)[:1000]
            await page.screenshot(path=str(root / 'failure.png'), full_page=True)
            raise
        finally:
            receipt['completed_at_utc'] = final.now()
            final.write_exclusive_json(root / 'receipt.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(smoke(args.output_dir))
