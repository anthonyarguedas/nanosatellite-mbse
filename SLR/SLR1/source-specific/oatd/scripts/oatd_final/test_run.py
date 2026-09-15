"""Focused regressions for native transport, metadata honesty, and final publication.

Saved live evidence is used only as an offline fixture. Temporary outputs never
contribute to the final review searches.
"""
from __future__ import annotations
import asyncio
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import run as final
import record_metadata

FIXTURES = final.DEFAULT_FINAL_ROOT / 'code-audit/native-transport-smoke'


class FinalOATDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = final.load_adapter()
        cls.queries = final.load_queries()
        cls.local_plan = cls.adapter.load_local_matching_plan(final.LOCAL_PLAN_PATH)

    def record(self):
        fixture = final.load(FIXTURES / 'detail-audit.json')
        record = deepcopy(fixture['record'])
        fields = {key: [] for key in record_metadata.DETAIL_FIELDS}
        for raw in fixture['dom']['type_degree_fields']:
            for key, labels in record_metadata.DETAIL_FIELDS.items():
                if raw['label'] in labels:
                    fields[key].append(raw)
        class Page:
            async def evaluate(self, script, labels):
                return {'fields': fields, 'abstract': [{'label': 'Abstract', 'value': record['abstract']}]}
        record['oatdDetail'] = asyncio.run(record_metadata.capture(Page(), record))
        record['rank'] = 1
        record['localMatching'], _ = self.adapter.annotate_local_matching_plan(record, self.local_plan)
        return record

    def test_native_transport_preserves_all_eight_exact_controlled_queries(self):
        for query in self.queries.GATE_QUERIES.values():
            controls = dict(language='English', year_start=2011, year_end=2026, page_size=30)
            original = self.adapter.build_oatd_search_configuration(query, **controls)
            native = final.build_configuration(self.adapter, query, **controls)
            route = parse_qs(urlsplit(self.adapter.build_search_url(query, configuration=native)).query)
            self.assertEqual(route, {'q': [original.route_query], 'form': ['basic']})
            self.assertEqual(native.effective_query, original.effective_query)

    def test_checkpoint_preserves_degree_metadata_and_flags_source_truncation(self):
        record = self.record()
        config = final.build_configuration(self.adapter, self.queries.GATE_QUERIES['G1-MH'],
                                           language='English', year_start=2011, year_end=2026)
        checkpoint = final.new_checkpoint('a' * 64, [record['paperId']], self.adapter)
        checkpoint = final.checkpoint_with_records(checkpoint, [record['paperId']], {record['paperId']: record})
        completed, records, ids = final.validate_checkpoint(
            self.adapter, checkpoint, plan_sha256='a' * 64, fresh_target_ids=[record['paperId']],
            configuration=config, local_plan=self.local_plan)
        self.assertEqual(completed, ids)
        materialized = final.materialize_record(records[ids[0]], rank=1)
        self.assertEqual(materialized['sourceDegreeLevel'], 'doctoral')
        self.assertEqual(materialized['sourceDegree'], 'PhD')
        self.assertEqual(materialized['abstract'], record['abstract'])
        summary = final.abstract_summary([materialized])
        self.assertEqual(summary['records_with_source_truncated_abstract'], 1)
        self.assertEqual(summary['records_with_full_source_abstract'], 0)
        self.assertFalse(summary['all_records_have_full_abstracts'])
        record['abstract'] += ' invented continuation'
        with self.assertRaises(RuntimeError):
            final.materialize_record(record, rank=1)

    def test_continuation_restores_only_complete_final_passes(self):
        import continue_native
        events = [final.plan_event(self.adapter, gid, query) for gid, query in self.queries.GATE_QUERIES.items()]
        first, second, images, bindings = continue_native.initial_evidence(self.adapter, events)
        self.assertEqual(len(first) + len(second), 16)
        self.assertEqual(len(bindings), 32)
        ids, cards, _ = final.target_union(first, events, self.adapter)
        self.assertEqual(len(ids), 27)
        self.assertTrue(all(card.detail_record_parameter == '' for card in cards.values()))
        self.assertTrue(all(set(images[gid]) == {'search_page', 'results_page'} for gid in first))
        for gid in first:
            self.assertEqual(set(first[gid].ordered_record_ids), set(second[gid].ordered_record_ids))

    def test_three_pass_gate_and_mergeable_union_publication_offline(self):
        a = self.adapter
        record = self.record()
        card = a.OATDSharedPopulationCard(record['paperId'], 'handle\\:1721.1/98586', record['title'], 1)
        snapshot = a.OATDSharedPopulationSnapshot(1, 1, 1, (card,), 30, ())
        screenshot_fixture = final.load(FIXTURES / 'gate.json')['screenshots']
        with tempfile.TemporaryDirectory(prefix='oatd-offline-test-') as directory:
            root = Path(directory)
            with patch.multiple(final, FINAL_ROOT=root, PLAN_PATH=root / 'plan.json',
                                CHECKPOINT_PATH=root / 'checkpoint.json', UNION_PATH=root / 'hydrated-union.json'):
                checkpoint = final.new_checkpoint('a' * 64, [record['paperId']], a)
                checkpoint = final.checkpoint_with_records(checkpoint, [record['paperId']], {record['paperId']: record})
                final.write_exclusive_json(final.CHECKPOINT_PATH, checkpoint)
                gates = {}
                membership = {record['paperId']: [{'event_id': event_id} for event_id in self.queries.GATE_IDS]}
                for event_id in self.queries.GATE_IDS:
                    event = final.plan_event(a, event_id, self.queries.GATE_QUERIES[event_id])
                    output = root / event['output']
                    paths = a.screenshot_paths_for_output(output)
                    payloads = {}
                    for kind, path in paths.__dict__.items():
                        evidence = deepcopy(screenshot_fixture[kind])
                        data = (FIXTURES / evidence['file_name']).read_bytes()
                        evidence['file_name'] = path.name
                        payloads[kind] = a._OATDScreenshotPayload(data, evidence)
                    artifact = final.build_gate_artifact(a, event, snapshot, snapshot, snapshot, payloads,
                        {record['paperId']: record}, membership, initial_retries=0, confirmation_retries=0)
                    final.publish_gate(a, output, artifact, payloads)
                    gates[event_id] = final.validate_gate(a, output)
                union = final.build_union_result(a, self.queries, {'candidate_route': {'identity': self.queries.ALGEBRAIC_IDENTITY}},
                    checkpoint, membership, gates, completed_at=final.now(), detail_requests_this_attempt=1, detail_busy_retries=0)
                published = final.publish_union(a, union)
                self.assertTrue(a.verify_commit_gated_publication(final.UNION_PATH, published, artifact_sha256=final.digest(final.UNION_PATH)))
                self.assertEqual(published['confirmation']['complete_source_pass_count'], 24)
                self.assertEqual(published['results'][0]['abstract'], record['abstract'])
                self.assertEqual(published['results'][0]['sourceDegreeLevel'], 'doctoral')
                self.assertEqual(published['results'][0]['publicationType'], 'Thesis or dissertation')


if __name__ == '__main__':
    unittest.main()
