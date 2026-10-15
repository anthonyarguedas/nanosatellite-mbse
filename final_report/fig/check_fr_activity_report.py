#!/usr/bin/env python3
"""Check Appendix D in an externally built full report.

python3 final_report/fig/check_fr_activity_report.py --builddir /absolute/external/build

Checks visible trace IDs, same-page captions, consecutive panel pages, actual
final-size trace fonts, page clipping, appendix registration and main-text size.
Writes inspection data only to the external build directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from diagram_style import require, run

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent


def bounds(pdf, target):
    run(['pdftotext', '-bbox', str(pdf), str(target)])
    # Existing Type 1 math glyphs can appear as XML-forbidden controls in
    # pdftotext output. Remove those controls for parsing, preserving the file.
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', target.read_text())
    return ET.fromstring(text).findall('.//{*}page')


def word_height(word):
    return float(word.attrib['yMax'])-float(word.attrib['yMin'])


def check(build):
    build = Path(build).resolve()
    require(not build.is_relative_to(ROOT), 'Use an external report build directory')
    job = build / 'fr-activity-inspection'
    job.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((FIG / 'fr-activity-flows.provenance.json').read_text())
    pages = bounds(build / 'main.pdf', job / 'report-bounds.html')
    appendix = (build / 'fr-activity-flows.aux').read_text()
    require(re.search(r'\\newlabel\{appendix:fr-activity-flows\}\{\{D\}', appendix),
            'Functional requirement flows are not Appendix D')
    labels = re.findall(r'\\newlabel\{fig:fr-flow-(\d\d)\}\{\{D\.(\d+)\}\{(\d+)\}', appendix)
    require(len(labels) == len(manifest['panels']), 'Missing compiled panel label')
    require([int(number) for _, number, _ in labels] == list(range(1, len(labels)+1)),
            'Changed figure numbering')
    printed = [int(page) for _, _, page in labels]
    require(printed == list(range(printed[0], printed[0]+len(printed))),
            'Panels have split or blank report pages between them')
    conclusion = (build / 'conclusiones.aux').read_text()
    main_end = int(re.search(r'\\setcounter\{page\}\{(\d+)\}', conclusion).group(1))-1
    require(main_end <= 70, 'Main text exceeds 70 pages')
    all_words = [page.findall('./{*}word') for page in pages]
    inspected = []
    for record, (prefix, number, printed_page) in zip(manifest['panels'], labels):
        require(record['id'].startswith(prefix+'-'), 'Changed panel order')
        ids = [record['id'][:2]+'.'+node['id'] for node in record['nodes'] if node['kind'] != 'external']
        matches = [i for i, words in enumerate(all_words)
                   if any(word.text == ids[0] for word in words)]
        require(len(matches) == 1, 'Panel identifier is missing / duplicated across report pages')
        index = matches[0]
        page, words = pages[index], all_words[index]
        text = ' '.join(word.text or '' for word in words)
        require('Figure D.'+number+':' in text, 'Panel caption is on a different page')
        for word in words:
            require(0 <= float(word.attrib['xMin']) <= float(word.attrib['xMax']) <= float(page.attrib['width'])
                    and 0 <= float(word.attrib['yMin']) <= float(word.attrib['yMax']) <= float(page.attrib['height']),
                    'Report text is clipped')
        for fr in record['checks']['visible_frs']:
            require(fr in text, 'FR identifier disappeared in the compiled report: '+fr)
        source = bounds(FIG / (record['file']+'.pdf'), job / (record['id']+'-bounds.html'))[0]
        source_words = source.findall('./{*}word')
        final_fonts = []
        for identifier in ids:
            src = [word for word in source_words if word.text == identifier]
            dst = [word for word in words if word.text == identifier]
            require(len(src) == len(dst) == 1, 'Missing / repeated visible activity ID: '+identifier)
            # Trace headers are the smallest source text at 22 PDF points.
            final_font = 22 * word_height(dst[0]) / word_height(src[0])
            require(final_font >= 9, 'Final-size identifier is below 9 pt')
            final_fonts.append(final_font)
        inspected.append(dict(panel=record['id'], printed_page=int(printed_page),
                              pdf_page=index+1, visible_activity_ids=ids,
                              minimum_trace_font_pt=round(min(final_fonts), 2)))
    actual_pages = [item['pdf_page'] for item in inspected]
    require(actual_pages == list(range(actual_pages[0], actual_pages[0]+len(actual_pages))),
            'Actual PDF panel pages are not consecutive')
    log = (build / 'main.log').read_text()
    overfull = re.findall(r'Overfull \\[hv]box[^\n]*', log)
    require(len(overfull) == 2 and all('hbox' in line for line in overfull),
            'Unexpected new overfull report box')
    result = dict(appendix='D', panels=len(inspected), actual_fr_count=len(manifest['coverage']),
                  main_text_last_printed_page=main_end, total_pdf_pages=len(pages),
                  minimum_trace_font_pt=min(item['minimum_trace_font_pt'] for item in inspected),
                  consecutive_panel_pages=True, captions_on_panel_pages=True,
                  no_clipped_appendix_words=True, existing_overfull_heading_count=len(overfull),
                  inspected_panels=inspected)
    (job / 'report-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--builddir', required=True, type=Path)
    args = parser.parse_args()
    result = check(args.builddir)
    print(json.dumps({key: value for key, value in result.items() if key != 'inspected_panels'}, indent=2))


if __name__ == '__main__':
    main()
