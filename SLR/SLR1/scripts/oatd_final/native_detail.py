"""Read Record Details by keyboard activation of a validated native result link."""
from __future__ import annotations
import re
from typing import Any
from urllib.parse import urlencode, urlsplit

import record_metadata
import source_native


async def read_by_id(adapter: Any, page: Any, *, card: Any, configuration: Any, local_plan: Any) -> dict:
    """Read one already gated ID without the large query-highlighting context.

    The full gate queries supply language/date/semantic membership evidence.
    Record Details lookup uses the observed stable ID. A bounded live comparison
    recovered the same MIT metadata with q empty after full-q detail failures.
    This operation performs no additional discovery search.
    """
    if not adapter._is_safe_detail_record_parameter(card.detail_record_parameter):
        raise RuntimeError('The detail lookup lacks an observed safe source identifier')
    url = adapter.SOURCE_ORIGIN + adapter.DETAIL_PATH + '?' + urlencode({
        'record': card.detail_record_parameter, 'q': ''})
    await adapter.navigate(page, url, 180)
    await source_native.observe(page, 180)
    await page.screenshot(full_page=True, timeout=30000)
    payload = await adapter.wait_ready(page, adapter.OATD_DETAIL_STATE_SCRIPT, {'query': ''}, 180)
    detail = adapter.parse_detail_state(payload, query='', expected_record_parameter=card.detail_record_parameter)
    if detail.record_id != card.record_id or adapter._title_key(detail.title) != adapter._title_key(card.title):
        raise RuntimeError('Identity-only Record Details lookup changed the expected source record')
    record = adapter._normalized_record_from_detail(detail, {'rank': card.rank, 'title': card.title},
        publication_date_readback=adapter._publication_date_readback(detail.publication_date, configuration))
    evidence = await record_metadata.capture(page, record)
    discipline = evidence['fields']['discipline']
    if discipline:
        record['departmentDiscipline'] = discipline[0]['value']
        record['detailFieldStates']['discipline'] = 'present'
    record['localMatching'], _ = adapter.annotate_local_matching_plan(record, local_plan)
    record['oatdDetail'] = evidence
    return record


async def read(adapter: Any, page: Any, *, card: Any, row_index: int,
               configuration: Any, local_plan: Any, return_to_results: bool = True) -> dict:
    payload = await page.evaluate(adapter.OATD_RESULT_STATE_SCRIPT, adapter._result_state_argument(configuration))
    expected = adapter.parse_result_state(payload, query=configuration.effective_query,
                                         expected_start=1, configuration=configuration)
    row = expected.rows[row_index]
    observed_card = adapter._shared_card_from_row(row)
    if observed_card.record_id != card.record_id:
        raise RuntimeError('The native detail link no longer identifies the expected record')
    link = page.locator('.result:visible').nth(row_index).locator('p.shareIcon a:visible').filter(
        has_text=re.compile(r'^\s*Record Details\s*$'))
    if await link.count() != 1:
        raise RuntimeError('Record Details link is missing or ambiguous')
    async with page.expect_navigation(url=lambda url: urlsplit(url).path == adapter.DETAIL_PATH,
                                      wait_until='domcontentloaded', timeout=180000):
        await link.press('Enter', timeout=180000)
    await source_native.observe(page, 180)
    await page.screenshot(full_page=True, timeout=30000)
    payload = await adapter.wait_ready(page, adapter.OATD_DETAIL_STATE_SCRIPT,
                                       {'query': configuration.effective_query}, 180)
    detail = adapter.parse_detail_state(payload, query=configuration.effective_query,
                                         expected_record_parameter=observed_card.detail_record_parameter)
    if detail.record_id != card.record_id or adapter._title_key(detail.title) != adapter._title_key(card.title):
        raise RuntimeError('Native Record Details identity changed')
    record = adapter._normalized_record_from_detail(detail, row,
        publication_date_readback=adapter._publication_date_readback(detail.publication_date, configuration))
    evidence = await record_metadata.capture(page, record)
    discipline = evidence['fields']['discipline']
    if discipline:
        record['departmentDiscipline'] = discipline[0]['value']
        record['detailFieldStates']['discipline'] = 'present'
    record['localMatching'], _ = adapter.annotate_local_matching_plan(record, local_plan)
    record['oatdDetail'] = evidence
    if return_to_results:
        await adapter.return_to_results(page, query=configuration.effective_query,
            expected_page=expected, timeout_seconds=180, configuration=configuration)
    return record
