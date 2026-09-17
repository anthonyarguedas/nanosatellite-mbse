"""Native form submission with the existing OATD parser and completeness checks.

The UI sequence follows the independently successful diagnostic. Search metadata
parsing begins only after the rendered native submission has been observed.
"""
from __future__ import annotations
import asyncio
from typing import Any

# This bounded projection observes visible forms, source text, and challenges.
from diagnose import STATE


async def observe(page: Any, timeout_seconds: float) -> dict:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while True:
        try:
            state = await page.evaluate(STATE)
        except Exception:
            if asyncio.get_running_loop().time() >= deadline:
                raise
            await asyncio.sleep(0.1)
            continue
        if not state['challenge'] or asyncio.get_running_loop().time() >= deadline:
            return state
        await asyncio.sleep(2)


async def collect(adapter: Any, page: Any, *, configuration: Any, limit: int,
                  max_pages: int, timeout_seconds: float, page_delay_seconds: float,
                  budget: Any, screenshot_paths: Any = None) -> tuple[Any, dict]:
    await page.goto('https://oatd.org/', wait_until='domcontentloaded', timeout=int(timeout_seconds * 1000))
    home = await observe(page, timeout_seconds)
    # Observe the rendered home page before interacting with its native form.
    await page.screenshot(full_page=True, timeout=30000)
    if home['challenge']:
        raise adapter.OATDMetadataAccessError('OATD access challenge remained before native form submission')
    form = page.locator('form#simpleForm')
    if await form.count() != 1:
        raise RuntimeError('OATD did not expose exactly one native basic form')
    form_state = next(value for value in home['forms'] if value['id'] == 'simpleForm')
    if form_state['method'] != 'get' or form_state['action_path'] != '/oatd/search':
        raise RuntimeError('OATD native basic form action changed')
    query_input = form.locator('input[name=q]')
    await query_input.fill(configuration.route_query)
    configured_state = await observe(page, timeout_seconds)
    if await query_input.input_value() != configuration.route_query:
        raise RuntimeError('Native OATD form lost the complete controlled query')
    search_png = await page.screenshot(full_page=True, timeout=30000)
    async with page.expect_navigation(wait_until='domcontentloaded', timeout=int(timeout_seconds * 1000)):
        await query_input.press('Enter')
    rendered = await observe(page, timeout_seconds)
    # Match the independent diagnostic's rendered observation before parsing.
    await page.screenshot(full_page=True, timeout=30000)
    if rendered['challenge']:
        raise adapter.OATDMetadataAccessError('OATD access challenge remained after native form submission')
    state = await adapter.wait_ready(
        page, adapter.OATD_RESULT_STATE_SCRIPT, adapter._result_state_argument(configuration),
        timeout_seconds, busy_retry_budget=budget,
        busy_retry_route=adapter._search_busy_retry_route(configuration, 1))
    current = adapter.parse_result_state(state, query=configuration.effective_query,
                                         expected_start=1, configuration=configuration)
    payloads = {}
    if screenshot_paths is not None:
        # OATD's anonymous home form contains no account identity or record data.
        evidence = {
            'page': 'configured_search_page', 'file_name': screenshot_paths.search_page.name,
            'sha256': adapter.hashlib.sha256(search_png).hexdigest(),
            **adapter._oatd_png_dimensions(search_png),
            'email_elements_masked': 0, 'account_elements_masked': 0,
            'full_page': True, 'browser_chrome_captured': False,
            'complete_page_url_retained': False, 'session_identifiers_retained': False,
            'configured_controls': {'form': 'source_basic_search',
                'query_submitted_from_screenshot_form': True,
                'effective_query_in_form': configuration.route_query,
                'effective_query_exact': True, 'native_form_parameter': 'basic',
                'typed_controls_verified_on_results_page': True},
        }
        payloads['search_page'] = adapter._OATDScreenshotPayload(search_png, evidence)
    await adapter._capture_verified_results_screenshot(
        page, paths=screenshot_paths, payloads=payloads if screenshot_paths else None,
        result_page=current, configuration=configuration)
    total = current.total
    if total > limit or adapter._required_page_count(total, configuration.page_size) > max_pages:
        raise RuntimeError('Native OATD result exceeds the declared complete-capture bound')
    cards = []
    ids = set()
    pages = 0
    facets = current.facets
    while True:
        pages += 1
        for row in current.rows:
            card = adapter._shared_card_from_row(row)
            if card.record_id in ids:
                raise RuntimeError('Native OATD traversal repeated a stable record ID')
            ids.add(card.record_id)
            cards.append(card)
        if len(cards) == total:
            break
        if len(cards) > total or current.next_start is None:
            raise RuntimeError('Native OATD traversal did not reach exact source exhaustion')
        current = await adapter.advance_to_next_page(
            page, query=configuration.effective_query, current_page=current,
            timeout_seconds=timeout_seconds, page_delay_seconds=page_delay_seconds,
            busy_retry_budget=budget, configuration=configuration)
    snapshot = adapter.OATDSharedPopulationSnapshot(total, pages, len(cards), tuple(cards),
                                                   configuration.page_size, facets)
    adapter._assert_complete_shared_population_snapshot(snapshot)
    return snapshot, payloads
