"""Offline regression for complete abstracts, source identity, and no new records."""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest

import enrich_abstracts as enrichment
import record_metadata


class EnrichmentTest(unittest.TestCase):
    def test_saved_repository_evidence_extends_every_incomplete_fixture_abstract(self):
        # Historical records are offline fixtures only. All outputs are temporary.
        pilot = enrichment.FINAL.parent / 'pilots/007/searches/hydrated-union.json'
        fixture = json.loads(pilot.read_text())
        source = {'total': fixture['total'], 'results': deepcopy(fixture['results']),
                  'output_metadata': {'merge_eligible': True}}
        for record in source['results']:
            record['publicationType'] = record['documentType']
            record['oatdDetail'] = {'abstract_state': record_metadata.abstract_state(record['abstract'])}
        with tempfile.TemporaryDirectory(prefix='oatd-enrichment-test-') as directory:
            root = Path(directory)
            enrichment.save(root / 'hydrated-union.json', source)
            enrichment.save(root / 'validation-report.json', {'status': 'valid', 'validated_source_pass_count': 24})
            result = enrichment.enrich(root)
            self.assertEqual(result['summary']['records_with_full_abstracts'], 26)
            self.assertEqual(result['summary']['repository_enriched_records'], 9)
            self.assertEqual(result['summary']['records_with_publication_types'], 26)
            self.assertFalse(result['merge_eligible'])
            self.assertFalse(result['additional_discovery_event'])
            self.assertEqual([r['paperId'] for r in result['records']], [r['paperId'] for r in source['results']])
            original = {r['paperId']: r for r in source['results']}
            for record in result['records']:
                self.assertEqual(record['oatdAbstract'], original[record['paperId']]['abstract'])
                self.assertEqual(record['abstractProvenance']['abstract_sha256'], enrichment.text_sha(record['abstract']))
            keio = next(r for r in result['records'] if r['paperId'] == 'oai:irdb.nii.ac.jp:0050/00050689')
            self.assertEqual(keio['repositoryPublicationType'], "Master's Dissertation")
            self.assertNotIn('Student Identification', keio['abstract'])
            self.assertNotIn('Key Words', keio['abstract'])


if __name__ == '__main__':
    unittest.main()
