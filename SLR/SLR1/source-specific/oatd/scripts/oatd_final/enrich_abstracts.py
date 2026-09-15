#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Join full repository abstracts to a complete OATD union without new discoveries.

Input text was fetched from public repository links during the code audit. The
join verifies titles and the entire normalized OATD abstract prefix. Originals,
source hashes, locations, and retrieval times remain in the output. This is a
metadata sidecar, never an additional mergeable search event.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import unicodedata
from copy import deepcopy
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[5]
FINAL = HERE.parents[3] / 'source-specific/oatd/final-searches'
EVIDENCE = FINAL / 'code-audit/repository-feasibility'


def normalized(text: str) -> str:
    return ' '.join(text.split())


def key(text: str) -> str:
    return re.sub(r'\W+', '', unicodedata.normalize('NFKC', html.unescape(text)).casefold())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write('\n')


def provenance(path: Path, url: str, locator: str, method: str, retrieved: str | None = None) -> dict:
    return {'source_url': url, 'capture_method': method, 'source_locator': locator,
            'retrieved_at_utc': retrieved or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            'evidence_path': str(path.relative_to(REPOSITORY)), 'evidence_sha256': sha(path)}


def markdown(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding='utf-8')
    front, body = text.removeprefix('---\n').split('\n---\n', 1)
    metadata = {}
    for line in front.splitlines():
        name, value = line.split(':', 1)
        try:
            metadata[name] = json.loads(value.strip())
        except json.JSONDecodeError:
            metadata[name] = value.strip()
    if metadata.get('http_status') != 200:
        raise RuntimeError('Repository metadata was not a successful response')
    return metadata, body


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def repository_candidates() -> list[dict]:
    values = []
    dspace = [
        ('mit.md', ['handle:1721.1/98586'], '\nAbstract\n\n', '\n\nDescription\n', 'Abstract'),
        ('csu-cybersecurity.md', ['handle:10217/241075', 'oai:mountainscholar.org:10217/241075'],
         '\n## Abstract\n\n', None, 'Abstract'),
        ('csu-evapotranspiration.md', ['handle:10217/239213', 'oai:mountainscholar.org:10217/239213'],
         '\n## Abstract\n\n', '\n\n## Description', 'Abstract'),
        ('cornell.md', ['handle:1813/67549'], None, None, 'Item description (abstract)'),
    ]
    for name, ids, start, end, locator in dspace:
        path = EVIDENCE / name
        meta, body = markdown(path)
        if start:
            if body.count(start) != 1:
                raise RuntimeError(f'Ambiguous abstract start in {path}')
            abstract = body.split(start, 1)[1]
        else:
            heading = '\n# ' + meta['title'] + '\n\n'
            if body.count(heading) != 1:
                raise RuntimeError('Cornell title/description boundary changed')
            abstract = body.split(heading, 1)[1]
            # The extracted Cornell item repeats its title before the abstract.
            repeated_title = meta['title'] + '\n\n'
            if not abstract.startswith(repeated_title):
                raise RuntimeError('Cornell repeated title boundary changed')
            abstract = abstract[len(repeated_title):]
        if end:
            if abstract.count(end) != 1:
                raise RuntimeError(f'Ambiguous abstract end in {path}')
            abstract = abstract.split(end, 1)[0]
        abstract = normalized(abstract)
        values.append({'record_ids': ids, 'title': meta['title'], 'abstract': abstract,
                       'publication_type': None,
                       'provenance': provenance(path, meta['final_url'], locator,
                                                'static_repository_metadata', meta['extracted_at'])})

    path = EVIDENCE / 'wollongong-api.md'
    meta, body = markdown(path)
    api = json.loads(body.split('```json\n', 1)[1].rsplit('\n```', 1)[0])
    parser = Text()
    parser.feed(api['description'])
    thesis_type = next(f['value'] for f in api['custom_fields'] if f['name'] == 'Thesis type')
    values.append({'record_ids': ['handle:10779/uow.27655986.v1'], 'title': api['title'],
                   'abstract': normalized(''.join(parser.parts)), 'publication_type': thesis_type,
                   'provenance': provenance(path, meta['final_url'], 'description and custom_fields[Thesis type]',
                                            'public_figshare_item_metadata', meta['extracted_at'])})

    path = EVIDENCE / 'kyutech-metadata.txt'
    text = path.read_text(encoding='utf-8')
    abstract = text.split('\n抄録\n内容記述タイプ\nAbstract\n内容記述\n', 1)[1].split('\n目次\n', 1)[0]
    title = text.split('\nタイトル\nタイトル\n', 1)[1].split('\n言語\n', 1)[0]
    source_type = text.split('\n資源タイプ\n', 2)[2].split('\n', 1)[0]
    if source_type != 'doctoral thesis':
        raise RuntimeError('Kyutech native resource type changed')
    values.append({'record_ids': ['oai:kyutech.repo.nii.ac.jp:00006740'], 'title': title,
                   'abstract': normalized(abstract), 'publication_type': source_type,
                   'oatd_abstract_start': 'Due to compact design, cost-effectiveness and shorter development time',
                   'provenance': provenance(path, 'https://kyutech.repo.nii.ac.jp/records/6740',
                                            '抄録 / Abstract, and 資源タイプ / Resource type', 'static_repository_metadata')})

    path = EVIDENCE / 'keio-front-matter.txt'
    pages = path.read_text(encoding='utf-8').split('\f')
    page = pages[2]
    title = normalized(page.split('\nTitle\n', 1)[1].split('\nAbstract\n', 1)[0])
    abstract = normalized(page.split('\nAbstract\n', 1)[1].split('\nKey Words', 1)[0])
    if "Master's Dissertation" not in pages[1]:
        raise RuntimeError('Keio source degree evidence is missing')
    evidence = provenance(path, 'https://koara.lib.keio.ac.jp/xoonips/modules/xoonips/download.php/KO40002001-00002015-0007.pdf?file_id=105060',
                          'PDF page 3, Abstract through the end before Key Words. Type on PDF page 2.',
                          'repository_pdf_abstract_text_extraction')
    pdf = EVIDENCE / 'keio.pdf'
    evidence.update({'pdf_path': str(pdf.relative_to(REPOSITORY)), 'pdf_sha256': sha(pdf),
                     'pdf_pages_used': [2, 3], 'ocr_used': False,
                     'extraction_command': 'pdftotext -f 1 -l 8 -layout keio.pdf keio-front-matter.txt'})
    values.append({'record_ids': ['oai:irdb.nii.ac.jp:0050/00050689'], 'title': title,
                   'abstract': abstract, 'publication_type': "Master's Dissertation", 'provenance': evidence})
    for value in values:
        if len(value['abstract']) < 100 or value['abstract'].endswith(('…', '...')):
            raise RuntimeError('A repository abstract is missing or visibly truncated')
        value['abstract_sha256'] = text_sha(value['abstract'])
    return values


def enrich(root: Path) -> dict:
    source_path = root / 'hydrated-union.json'
    validation = json.loads((root / 'validation-report.json').read_text())
    if validation.get('status') != 'valid' or validation.get('validated_source_pass_count') != 24:
        raise RuntimeError('Enrichment requires a complete validated 24-pass OATD source union')
    source = json.loads(source_path.read_text())
    if not source.get('output_metadata', {}).get('merge_eligible'):
        raise RuntimeError('The base source union is not mergeable')
    candidates = repository_candidates()
    indexed = {record_id: candidate for candidate in candidates for record_id in candidate['record_ids']}
    records = []
    supplemented = []
    for original in source['results']:
        record = deepcopy(original)
        state = original['oatdDetail']['abstract_state']
        record['oatdAbstract'] = original['abstract']
        record['oatdAbstractState'] = state
        record['abstractProvenance'] = {'source': 'OATD Record Details', 'oatd_union_sha256': sha(source_path),
                                        'paperId': original['paperId'], 'abstract_sha256': text_sha(original['abstract'])}
        if state in ('absent_in_oatd', 'truncated_in_oatd'):
            candidate = indexed.get(record['paperId'])
            if candidate is None:
                raise RuntimeError(f"No complete repository abstract for {record['paperId']}")
            if key(record['title']) != key(candidate['title']):
                raise RuntimeError(f"Repository title mismatch for {record['paperId']}")
            oatd_abstract = record['abstract']
            # OATD concatenates a degree note and table of contents before this
            # Kyutech abstract. Match the exact repository-proven abstract start,
            # retain the preamble separately, and still verify the entire prefix.
            start = candidate.get('oatd_abstract_start')
            if start:
                if oatd_abstract.count(start) != 1:
                    raise RuntimeError('OATD compound description boundary changed')
                preamble, suffix = oatd_abstract.split(start, 1)
                record['oatdDescriptionPrefix'] = preamble
                oatd_abstract = start + suffix
            prefix = key(oatd_abstract.rstrip('… .'))
            if prefix and not key(candidate['abstract']).startswith(prefix):
                raise RuntimeError(f"Repository abstract does not extend the OATD prefix for {record['paperId']}")
            record['abstract'] = candidate['abstract']
            record['abstract_not_available'] = False
            record['abstractProvenance'] = deepcopy(candidate['provenance'])
            record['abstractProvenance'].update({'abstract_sha256': candidate['abstract_sha256'],
                                                 'repository_title': candidate['title'],
                                                 'identity_verified': 'normalized title and complete OATD prefix, when present'})
            record['repositoryPublicationType'] = candidate['publication_type']
            supplemented.append(record['paperId'])
        if not record['abstract'] or record['abstract'].endswith(('…', '...')):
            raise RuntimeError(f"Full abstract requirement remains unresolved for {record['paperId']}")
        record['abstractCompleteness'] = 'complete_as_provided_by_cited_source'
        records.append(record)
    if [r['paperId'] for r in records] != [r['paperId'] for r in source['results']]:
        raise RuntimeError('Metadata enrichment changed the source record set')
    return {
        'schema_version': 'slr1-oatd-full-abstract-enrichment/v1',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'source': 'OATD with linked repository abstract enrichment',
        'merge_eligible': False, 'additional_discovery_event': False,
        'usage': 'Join records to hydrated-union.json by paperId. Use abstract and abstractProvenance for complete text. Count only the original OATD discovery event.',
        'source_union': {'path': source_path.name, 'sha256': sha(source_path), 'records': source['total'],
                         'validation_sha256': sha(root / 'validation-report.json')},
        'script_sha256': sha(Path(__file__)),
        'records': records,
        'summary': {'records': len(records), 'records_with_full_abstracts': len(records),
                    'records_with_publication_types': sum(bool(r.get('publicationType')) for r in records),
                    'repository_enriched_records': len(supplemented), 'repository_enriched_ids': supplemented,
                    'record_ids_and_order_preserved': True, 'source_abstracts_preserved': True,
                    'reviewer_publication_type_assigned': False},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=FINAL / 'corrective-013')
    parser.add_argument('--check-candidates', action='store_true', help='Validate available repository evidence without reading or publishing a source union')
    args = parser.parse_args()
    if args.check_candidates:
        print(json.dumps([{'record_ids': c['record_ids'], 'title': c['title'], 'abstract_characters': len(c['abstract'])}
                          for c in repository_candidates()], ensure_ascii=False, indent=2))
    else:
        artifact = enrich(args.root)
        path = args.root / 'full-abstracts.json'
        save(path, artifact)
        print(json.dumps({'saved': str(path), **artifact['summary']}))
