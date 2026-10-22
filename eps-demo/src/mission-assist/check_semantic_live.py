#!/usr/bin/env python3
"""Explicit live smoke test against the optional local service and reviewed catalogue.

Uses synthetic queries only. No API keys, remote calls, downloads or index access.
"""
import argparse
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from serve_semantic import MODEL, REVISION

QUERIES = [
    ('Proba-V', 'Image vegetation across the Earth to monitor land cover and agriculture, then downlink the camera observations.'),
    ('RAX-2', 'Receive scattered ground radar signals from plasma irregularities in the polar ionosphere and store the measurements for later downlink.'),
    ('RainCube', 'Demonstrate a compact radar in a small satellite to measure precipitation and rain clouds from Earth orbit.'),
    ('ASTERIA', 'Observe nearby stars with a space telescope and measure their brightness precisely to detect exoplanet transits.'),
    ('UM5-SAT', 'Receive short messages from Internet of Things terminals across Morocco and relay the data to a ground station during contact windows.'),
]


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path, default=Path(__file__).resolve().parent.parent / 'data' / 'missions.json')
    parser.add_argument('--endpoint', default='http://127.0.0.1:8767/embed')
    args = parser.parse_args()
    if urlparse(args.endpoint).hostname not in {'127.0.0.1', 'localhost'}:
        parser.error('This test permits loopback endpoints only.')
    missions = json.loads(args.catalogue.read_text())['missions']
    documents = [mission['name'] + '. ' + mission['description'] for mission in missions]
    for expected, query in QUERIES + [(None, 'A satellite will bake delicious pizza and prepare tomato pasta for dinner.')]:
        body = json.dumps({'query': query, 'documents': documents}).encode()
        request = Request(args.endpoint, data=body, headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
        assert result['model'] == MODEL and result['revision'] == REVISION
        vectors = [result['queryVector']] + result['documentVectors']
        assert len(result['documentVectors']) == len(missions)
        assert all(len(vector) == 1024 and all(math.isfinite(value) for value in vector) for vector in vectors)
        ranks = sorted(zip(missions, (cosine(result['queryVector'], vector) for vector in result['documentVectors'])), key=lambda pair: -pair[1])
        top, score = ranks[0]
        if expected is None:
            assert score < 0.55, f'Adversarial unrelated query clears threshold: {top["name"]} {score}'
            print(f'Unrelated satellite recipe: abstained (highest cosine {score:.3f})')
        else:
            assert top['name'].lower().startswith(expected.lower()) and score >= 0.55, f'Expected {expected}, got {top["name"]} {score}'
            print(f'{expected}: top analogue {top["name"]}, cosine {score:.3f}')
    print('6 live semantic smoke checks passed. These examples do not calibrate suitability.')


if __name__ == '__main__':
    main()
