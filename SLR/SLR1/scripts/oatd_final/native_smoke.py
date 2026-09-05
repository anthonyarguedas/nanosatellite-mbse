#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Opt-in native OATD gate smoke with durable failure evidence and owned-page cleanup."""
import argparse
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import run as final


async def main(root, gate_ids):
    root.mkdir(parents=True, exist_ok=False)
    adapter = final.load_adapter()
    queries = final.load_queries()
    events = [final.plan_event(adapter, gid, queries.GATE_QUERIES[gid]) for gid in gate_ids]
    final.write_exclusive_json(root / 'plan.json', {
        'created_at_utc': final.now(), 'merge_eligible': False, 'events': events,
        'submission': 'native form after load, one fill, directly created owned page per gate',
        'detail_requests': 0, 'inter_query_delay_seconds': 60,
        'driver_sha256': final.digest(final.SCRIPT_DIR / 'source_native.py'),
        'runner_sha256': final.digest(final.SCRIPT_PATH),
    })
    receipt = {'merge_eligible': False, 'started_at_utc': final.now(), 'completed': []}
    try:
        async with async_playwright() as pw, adapter._LeaseCleanup() as cleanup:
            cleanup.lease, _ = await final.acquire_shared_profile_lease(adapter, pw, {})
            for index, event in enumerate(events):
                if index:
                    await asyncio.sleep(60)
                    await final.replace_owned_gate_page(adapter, cleanup.lease)
                page = cleanup.lease.page
                try:
                    snapshot, config, payloads, _ = await final.capture_snapshot(
                        adapter, page, event, output=root / (event['event_id'] + '.json'))
                    for payload in payloads.values():
                        final.write_exclusive_bytes(root / payload.evidence['file_name'], payload.data)
                    final.write_exclusive_json(root / (event['event_id'] + '.json'), {
                        'merge_eligible': False, 'captured_at_utc': final.now(),
                        'query': config.effective_query, 'snapshot': final.snapshot_payload(adapter, snapshot),
                        'screenshots': {key: value.evidence for key, value in payloads.items()},
                    })
                    receipt['completed'].append({'event': event['event_id'], 'total': snapshot.total})
                    print(json.dumps(receipt['completed'][-1]), flush=True)
                except Exception as error:
                    await page.screenshot(path=str(root / (event['event_id'] + '-failure.png')), full_page=True)
                    receipt.update({'error_type': type(error).__name__, 'error': str(error)[:1000]})
                    raise
        receipt.update({'status': 'complete', 'owned_pages_closed': True})
    finally:
        receipt['completed_at_utc'] = final.now()
        final.write_exclusive_json(root / 'receipt.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--gates', nargs='+', required=True)
    args = parser.parse_args()
    asyncio.run(main(args.output_dir, args.gates))
