#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Continue from the 16 complete final gate passes, using native detail links.

No pilot record is reused. The prior final pass files and screenshots are bound
before execution. Every detail-context set and final confirming set must match
both retained initial passes. All final publication uses the normal validator.
"""
from __future__ import annotations
import argparse
import asyncio
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright
import run as final
import native_detail
import source_native

PRIOR = final.DEFAULT_FINAL_ROOT / 'corrective-009'
ROOT = final.DEFAULT_FINAL_ROOT / 'corrective-013'
PRIOR_CHECKPOINT = final.DEFAULT_FINAL_ROOT / 'corrective-012/checkpoint/hydrated-union.checkpoint.json'
PRIOR_PLAN = final.DEFAULT_FINAL_ROOT / 'corrective-012/final-event-plan.json'


def initial_evidence(adapter: Any, events: list[dict]) -> tuple[dict, dict, dict, dict]:
    first, second, images, bindings = {}, {}, {}, {}
    for event in events:
        event_id = event['event_id']
        observations = []
        for number in (1, 2):
            path = PRIOR / 'progress' / event_id / f'pass-{number:02d}' / 'snapshot.json'
            value = final.load(path)
            if (value.get('event_id') != event_id or value.get('pass_number') != number
                    or value.get('requested_query') != event['query']
                    or value.get('executed_query') != event['effective_query']):
                raise RuntimeError('Retained initial pass does not match the exact final query')
            payload = value['snapshot']
            # Empty route parameters make these historical cards non-navigable.
            # Details use only links observed again on a fresh native gate page.
            cards = tuple(adapter.OATDSharedPopulationCard(c['paperId'], '', c['title'], c['rank'])
                          for c in payload['cards'])
            snapshot = adapter.OATDSharedPopulationSnapshot(payload['source_reported_total'],
                payload['pages_retrieved'], payload['source_card_rows_seen'], cards, payload['page_size'], ())
            adapter._assert_complete_shared_population_snapshot(snapshot)
            if final.snapshot_payload(adapter, snapshot) != payload:
                raise RuntimeError('Retained initial pass accounting or hashes are invalid')
            observations.append(snapshot)
            bindings[final.relative(path)] = final.digest(path)
            if number == 1:
                images[event_id] = {}
                for kind, evidence in value['screenshots'].items():
                    image = path.parent / evidence['file_name']
                    if final.digest(image) != evidence['sha256']:
                        raise RuntimeError('Retained initial screenshot changed')
                    images[event_id][kind] = adapter._OATDScreenshotPayload(image.read_bytes(), evidence)
                    bindings[final.relative(image)] = final.digest(image)
                if set(images[event_id]) != {'search_page', 'results_page'}:
                    raise RuntimeError('Retained initial pass lacks both screenshots')
        adapter.reconcile_shared_population_snapshots(*observations)
        first[event_id], second[event_id] = observations
    return first, second, images, bindings


def build_plan() -> dict:
    plan = final.build_plan()
    adapter = final.load_adapter()
    first, second, images, bindings = initial_evidence(adapter, plan['events'])
    plan['continuation'] = {
        'from_run_id': 'final-main-oatd-009',
        'retained_complete_initial_passes': 16,
        'retained_hydrated_records': 10,
        'retained_checkpoint': {
            'path': final.relative(PRIOR_CHECKPOINT), 'sha256': final.digest(PRIOR_CHECKPOINT),
            'plan_path': final.relative(PRIOR_PLAN), 'plan_sha256': final.digest(PRIOR_PLAN),
        },
        'source_pass_files': bindings,
        'earlier_failure_leaves_union_null_until_confirmation': True,
        'new_detail_transport': 'Native link with explicit detail-navigation wait. On HTTP 500/504, one stable-ID empty-q lookup after a 120-second wait. Both modes require exact ID and title readback.',
        'additional_detail_context_passes': 'Fresh gate pages used for native links, with equal stable ID sets required',
        'final_confirming_passes_required': 8,
        'pilot_records_reused': 0,
    }
    plan['execution_policy']['detail_hydration'] = 'one successful validated Record Details lookup per unique ID'
    plan['execution_policy']['detail_lookup_modes'] = ['native_full_gate_context', 'stable_id_empty_context']
    plan['execution_policy']['http_504_retry'] = True
    plan['execution_policy']['detail_http_fallback'] = {'statuses': [500, 504], 'maximum_alternate_attempts_per_record': 1,
                                                     'delay_seconds': 120, 'discovery_query_changed': False}
    return plan


async def workflow(adapter: Any, queries: Any, plan: dict, local_plan: Any, *, resume: bool) -> dict:
    events = plan['events']
    first, second, images, bindings = initial_evidence(adapter, events)
    if bindings != plan['continuation']['source_pass_files']:
        raise RuntimeError('Continuation source evidence changed after predeclaration')
    ids, _historical_cards, membership = final.target_union(first, events, adapter)
    config = {event['event_id']: final.build_configuration(adapter, event['query'], language='English',
              year_start=final.YEAR_START, year_end=final.YEAR_END, page_size=30) for event in events}
    event_map = {event['event_id']: event for event in events}
    if final.CHECKPOINT_PATH.exists():
        if not resume:
            raise RuntimeError('Use --resume for the existing continuation checkpoint')
        checkpoint = final.load(final.CHECKPOINT_PATH)
    else:
        binding = plan['continuation']['retained_checkpoint']
        if final.digest(PRIOR_CHECKPOINT) != binding['sha256'] or final.digest(PRIOR_PLAN) != binding['plan_sha256']:
            raise RuntimeError('The retained successful final detail checkpoint changed')
        prior = final.load(PRIOR_CHECKPOINT)
        _completed, prior_records, _ids = final.validate_checkpoint(adapter, prior,
            plan_sha256=binding['plan_sha256'], fresh_target_ids=ids,
            configuration=config[events[0]['event_id']], local_plan=local_plan)
        if len(prior_records) != plan['continuation']['retained_hydrated_records']:
            raise RuntimeError('The retained final detail count changed')
        checkpoint = final.new_checkpoint(final.digest(final.PLAN_PATH), ids, adapter)
        checkpoint = final.checkpoint_with_records(checkpoint, ids, prior_records)
    completed, records, ids = final.validate_checkpoint(adapter, checkpoint,
        plan_sha256=final.digest(final.PLAN_PATH), fresh_target_ids=ids,
        configuration=config[events[0]['event_id']], local_plan=local_plan)
    before = len(completed)
    final.write_atomic_json(final.CHECKPOINT_PATH, checkpoint)
    confirmations, confirmation_retries = {}, {}
    contexts = []
    policy = plan['execution_policy']
    async with async_playwright() as pw, adapter._LeaseCleanup() as cleanup:
        cleanup.lease, _ = await final.acquire_shared_profile_lease(adapter, pw, policy)
        page = cleanup.lease.page
        current_gate = None
        context_cards = {}
        for record_id in ids:
            if record_id in records:
                continue
            gate = membership[record_id][0]['gate_id']
            try:
                if current_gate != gate:
                    if contexts:
                        await asyncio.sleep(policy['inter_gate_delay_seconds'])
                        page = await final.replace_owned_gate_page(adapter, cleanup.lease)
                    snapshot, _config, _payloads, _retries = await final.capture_snapshot(
                        adapter, page, event_map[gate], persist_progress=True)
                    adapter.reconcile_shared_population_snapshots(first[gate], snapshot)
                    adapter.reconcile_shared_population_snapshots(second[gate], snapshot)
                    if snapshot.pages_retrieved != 1:
                        raise RuntimeError('The native detail context requires the observed single-page gate bound')
                    context_cards = {card.record_id: (index, card) for index, card in enumerate(snapshot.cards)}
                    current_gate = gate
                    contexts.append({'gate_id': gate, 'source_total': snapshot.total,
                                     'stable_ids_sha256': adapter._stable_record_ids_sha256(snapshot.ordered_record_ids)})
                index, card = context_cards[record_id]
                state = await page.evaluate(adapter.OATD_RESULT_STATE_SCRIPT, adapter._result_state_argument(config[gate]))
                expected_page = adapter.parse_result_state(state, query=config[gate].effective_query,
                                                           expected_start=1, configuration=config[gate])
                lookup_mode = 'native_full_gate_context'
                try:
                    record = await native_detail.read(adapter, page, card=card, row_index=index,
                        configuration=config[gate], local_plan=local_plan, return_to_results=False)
                except adapter.OATDMetadataRequestError as error:
                    if not any(f'HTTP {status}' in str(error) for status in (500, 504)):
                        raise
                    await final.save_failed_page(adapter, page, 'native-context-before-alternate', error)
                    await asyncio.sleep(policy['detail_http_fallback']['delay_seconds'])
                    lookup_mode = 'stable_id_empty_context'
                    record = await native_detail.read_by_id(adapter, page, card=card,
                        configuration=config[gate], local_plan=local_plan)
                record = final.validate_record(adapter, record, configuration=config[gate], local_plan=local_plan)
                records[record_id] = record
                checkpoint = final.checkpoint_with_records(checkpoint, ids, records)
                if adapter._checkpoint_has_unsafe_content(checkpoint):
                    raise RuntimeError('The native continuation checkpoint retained unsafe context')
                final.write_atomic_json(final.CHECKPOINT_PATH, checkpoint)
                print(__import__('json').dumps({'stage': 'native_detail_hydration', 'completed_records': len(records),
                                               'target_records': len(ids), 'paperId': record_id}), flush=True)
                remaining = len(ids) - len(records)
                if remaining:
                    if lookup_mode == 'native_full_gate_context':
                        await adapter.return_to_results(page, query=config[gate].effective_query,
                            expected_page=expected_page, timeout_seconds=180, configuration=config[gate])
                    else:
                        current_gate = None
                    delay = policy['detail_batch_cooldown_seconds'] if (len(records) - before) % policy['detail_batch_size'] == 0 else policy['detail_delay_seconds']
                    await asyncio.sleep(delay)
            except Exception as error:
                try:
                    await final.save_failed_page(adapter, page, 'native-detail-hydration', error)
                except Exception:
                    pass
                raise
        final.write_exclusive_json(final.FINAL_ROOT / 'detail-context-passes.json', {
            'merge_eligible': False, 'passes': contexts, 'count': len(contexts),
            'purpose': 'Native detail link contexts, additional to the 24 required membership passes'})
        await asyncio.sleep(policy['pre_confirmation_delay_seconds'])
        for index, event in enumerate(events):
            if index:
                await asyncio.sleep(policy['inter_gate_delay_seconds'])
            page = await final.replace_owned_gate_page(adapter, cleanup.lease)
            confirmation, _config, _payloads, retries = await final.capture_snapshot(
                adapter, page, event, persist_progress=True)
            adapter.reconcile_shared_population_snapshots(first[event['event_id']], confirmation)
            adapter.reconcile_shared_population_snapshots(second[event['event_id']], confirmation)
            confirmations[event['event_id']] = confirmation
            confirmation_retries[event['event_id']] = retries
            print(__import__('json').dumps({'stage': 'confirming_gate_snapshot', 'event': event['event_id'],
                                          'total': confirmation.total}), flush=True)
    final.confirmation_membership(confirmations, events, membership)
    return {'events': events, 'snapshots': first, 'second_initials': second,
            'confirmations': confirmations, 'screenshot_payloads': images,
            'initial_retries': {event['event_id']: 0 for event in events},
            'confirmation_retries': confirmation_retries, 'checkpoint': checkpoint,
            'membership': membership, 'records_by_id': records, 'completed_before': before,
            'completed_after': len(records), 'detail_requests_this_attempt': len(records) - before,
            'detail_busy_retries': 0, 'shared_target_acquisition_retries': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'run'])
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    final.configure_final_root(ROOT)
    if args.command == 'plan':
        plan = build_plan()
        final.validate_plan(plan, require_empty_outputs=True)
        final.write_exclusive_json(final.PLAN_PATH, plan)
        print('Saved continuation plan:', final.PLAN_PATH)
    else:
        final.execute_workflow = workflow
        raise SystemExit(final.run(args.resume))
