#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Inspect one native OATD form submission without the search adapter.

This is implementation evidence only. It never hydrates records or publishes a
mergeable result. Run under agent-tools' shared-browser runner.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

from playwright.async_api import async_playwright


STATE = r"""() => {
  const text = value => String(value || '').replace(/\s+/g, ' ').trim();
  const forms = Array.from(document.querySelectorAll('form')).map(form => ({
    id: form.id, method: form.method,
    action_path: new URL(form.action).pathname,
    controls: Array.from(form.querySelectorAll('input, select')).map(input => ({
      tag: input.tagName, id: input.id, name: input.name, type: input.type,
      value: input.value,
      options: input.tagName === 'SELECT' ? Array.from(input.options).map(o => ({
        label: text(o.textContent), value: o.value
      })) : undefined
    }))
  }));
  const navigation = performance.getEntriesByType('navigation').at(-1);
  const title = text(document.title);
  const challenge = /just a moment|attention required|verify you are human/i.test(title) ||
    !!document.querySelector('#challenge-running, #challenge-form, iframe[src*="challenges.cloudflare.com"]');
  const report = document.querySelector('p.matchesReport');
  return {
    title, challenge, navigation_status: navigation?.responseStatus ?? null,
    forms, report: text(report?.textContent),
    detail_link_count: Array.from(document.querySelectorAll('a')).filter(a => text(a.textContent) === 'Record Details').length,
    visible_page_text: text(document.body?.innerText).slice(0, 12000)
  };
}"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def save(path: Path, value: dict) -> None:
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


async def run(output: Path, query: str, compare_adapter_route: bool) -> None:
    if os.environ.get('BH_BROWSER_ACCESS_CONTRACT') != 'shared-browser-owned-tabs-v1':
        raise RuntimeError('Use the shared-browser runner')
    endpoint = os.environ.get('BH_CDP_URL', '')
    if endpoint != 'http://127.0.0.1:9222':
        raise RuntimeError('The diagnostic requires the canonical shared endpoint')
    output.mkdir(parents=True, exist_ok=False)
    save(output / 'plan.json', {
        'schema_version': 'slr1-oatd-native-route-diagnostic/v1',
        'created_at_utc': now(), 'merge_eligible': False,
        'purpose': 'Independent native UI check of adapter route and error classification',
        'query': query, 'entrypoint': 'https://oatd.org/',
        'submission': 'Fill the source basic q field and submit its native form once',
        'controls': 'Any language and date clauses are preserved literally in q',
        'compare_adapter_route_without_form_parameter': compare_adapter_route,
        'comparison_delay_seconds': 60 if compare_adapter_route else None,
        'detail_requests': 0, 'automatic_retries': 0,
        'passive_challenge_timeout_seconds': 120,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    })
    receipt = {'started_at_utc': now(), 'merge_eligible': False, 'stages': [],
               'main_document_responses': [], 'owned_page_closed': False}
    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(endpoint)
        page = await browser.contexts[0].new_page()

        def response_seen(response):
            request = response.request
            if request.is_navigation_request() and request.frame == page.main_frame:
                parsed = urlsplit(response.url)
                params = parse_qs(parsed.query)
                receipt['main_document_responses'].append({
                    'observed_at_utc': now(), 'origin': f'{parsed.scheme}://{parsed.netloc}',
                    'path': parsed.path, 'status': response.status,
                    'query_exact': params.get('q') == [query],
                    'query_parameter_names': sorted(params),
                })

        page.on('response', response_seen)

        async def capture(stage):
            deadline = asyncio.get_running_loop().time() + 120
            while True:
                state = await page.evaluate(STATE)
                if not state['challenge'] or asyncio.get_running_loop().time() >= deadline:
                    break
                await asyncio.sleep(2)
            parsed = urlsplit(page.url)
            state.update({'stage': stage, 'captured_at_utc': now(),
                          'origin': f'{parsed.scheme}://{parsed.netloc}', 'path': parsed.path,
                          'query_exact': parse_qs(parsed.query).get('q') == [query]})
            png = await page.screenshot(full_page=True, timeout=30000)
            image = output / f'{stage}.png'
            with image.open('xb') as handle:
                handle.write(png)
            state['screenshot'] = {'file': image.name, 'bytes': len(png),
                                   'sha256': hashlib.sha256(png).hexdigest()}
            receipt['stages'].append(state)
            save(output / f'{stage}.json', state)
            print(json.dumps({key: state[key] for key in (
                'stage', 'title', 'path', 'navigation_status', 'query_exact', 'report',
                'detail_link_count', 'challenge')}), flush=True)
            return state

        try:
            await page.goto('https://oatd.org/', wait_until='domcontentloaded', timeout=180000)
            state = await capture('home')
            if state['challenge']:
                raise RuntimeError('Access challenge remained. No submission attempted.')
            form = page.locator('form#simpleForm')
            if await form.count() != 1:
                raise RuntimeError('The source basic form was not present')
            await form.locator('input[name=q]').fill(query)
            await capture('configured-search')
            async with page.expect_navigation(wait_until='domcontentloaded', timeout=180000):
                await form.locator('input[name=q]').press('Enter')
            state = await capture('native-results')
            if compare_adapter_route and not state['challenge']:
                # Change only the native form=basic parameter. Keep q identical.
                await asyncio.sleep(60)
                await page.goto('https://oatd.org/oatd/search?' + urlencode({'q': query}),
                                wait_until='domcontentloaded', timeout=180000)
                await capture('adapter-route-results')
        except Exception as error:
            receipt['error_type'] = type(error).__name__
            # Error messages from browser calls can contain opaque URLs. Keep only the type.
            try:
                await capture('failure-page')
            except Exception:
                receipt['failure_page_capture_failed'] = True
            raise
        finally:
            await page.close()
            receipt['owned_page_closed'] = page.is_closed()
            receipt['completed_at_utc'] = now()
            save(output / 'receipt.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--query', default='"CubeSat"')
    parser.add_argument('--compare-adapter-route', action='store_true')
    args = parser.parse_args()
    asyncio.run(run(args.output_dir, args.query, args.compare_adapter_route))
