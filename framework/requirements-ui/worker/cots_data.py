"""Trusted local COTS facts. Cache catalogue source data, never workspace values."""
import csv
import hashlib
import io
import json
import math
from functools import lru_cache
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parents[2] / 'cots'
FILES = ('products.tsv', 'definitions.tsv', 'parameters.tsv', 'features.tsv',
         'conditions.tsv', 'condition-parameters.tsv', 'sources.tsv', 'elements.tsv')
TYPES = {'Real': 'float', 'Integer': 'integer', 'Boolean': 'boolean', 'String': 'string'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


def scalar(text, kind):
    if kind == 'string':
        return text
    if kind == 'boolean':
        if text not in ('true', 'false'):
            raise ValueError('Catalogue Boolean facts must be true or false.')
        return text == 'true'
    value = float(text)
    if not math.isfinite(value) or kind == 'integer' and (not value.is_integer() or abs(value) > 9007199254740991):
        raise ValueError('Catalogue facts must contain finite, typed values.')
    return int(value) if kind == 'integer' else value


@lru_cache(maxsize=1)
def parse_catalog(sources):
    tables = {name: list(csv.DictReader(io.StringIO(text), delimiter='\t')) for name, text in zip(FILES, sources)}
    products = {row['product_id']: {**row, 'facts': []} for row in tables['products.tsv']}
    definitions = {}
    for row in tables['definitions.tsv']:
        key = (row['definition_kind'], row['name'])
        if key in definitions and definitions[key]['scalar_type'] != row['scalar_type']:
            raise ValueError('Conflicting COTS fact types.')
        definitions[key] = row
    conditions = {row['condition_id']: row for row in tables['conditions.tsv']}
    condition_parameters = {}
    for row in tables['condition-parameters.tsv']:
        condition_parameters.setdefault(row['condition_id'], []).append(row)
    provenance = {row['source_id']: row for row in tables['sources.tsv']}
    elements = {(row['product_id'], row['element_id']): row for row in tables['elements.tsv']}
    ids = set()
    for kind, file, column in (('parameter', 'parameters.tsv', 'parameter_name'), ('feature', 'features.tsv', 'feature_name')):
        for row in tables[file]:
            product, name, element = row['product_id'], row[column], row['element_id']
            definition = definitions.get((kind, name))
            source = provenance.get(row['source_id'])
            condition_id = row.get('condition_id', '')
            condition = conditions.get(condition_id) if condition_id else None
            if product not in products or definition is None or source is None or condition_id and condition is None:
                raise ValueError('A COTS fact has an unresolved product, definition, source or condition.')
            kind_type = TYPES[definition['scalar_type']]
            identity = [kind, product, element, name, row.get('value_kind', ''), condition_id, row['source_id'], row['source_locator']]
            identifier = digest(identity)
            if identifier in ids:
                raise ValueError('Ambiguous COTS fact identity. Distinguish its source or conditions.')
            ids.add(identifier)
            element_definition = elements.get((product, element), {'element_id': element})
            extra_conditions = []
            for item in condition_parameters.get(condition_id, []):
                condition_source = provenance.get(item['source_id'])
                if condition_source is None:
                    raise ValueError('An additional COTS condition has an unresolved source.')
                extra_conditions.append({**item, 'source_revision': condition_source['revision'],
                                         'source_sha256': condition_source['sha256'], 'source_url': condition_source['url']})
            revision = digest([row, definition, source, condition, extra_conditions, element_definition])
            products[product]['facts'].append({
                'id': identifier, 'revision': revision, 'name': name, 'element': element,
                'kind': kind, 'type': kind_type, 'unit': row.get('unit', ''),
                'valueKind': row.get('value_kind', 'declared'), 'value': scalar(row['value'], kind_type),
                'condition': {'id': condition_id, 'values': {key: value for key, value in (condition or {}).items() if key != 'condition_id' and value},
                              'parameters': extra_conditions},
                'source': {'id': row['source_id'], 'locator': row['source_locator'], 'url': source['url'],
                           'revision': source['revision'], 'sha256': source['sha256'], 'retrievedUtc': source['retrieved_utc']},
            })
    for product in products.values():
        product['facts'].sort(key=lambda fact: (fact['element'] != 'self', fact['element'], fact['name'], fact['valueKind'], fact['condition']['id'], fact['id']))
    return products


def catalog():
    # Content-keyed caching detects external edits even when timestamps repeat.
    return parse_catalog(tuple((DIRECTORY / name).read_text(encoding='utf-8') for name in FILES))


def product_facts(product_id):
    product = catalog().get(product_id)
    if product is None:
        raise ValueError('Choose an existing COTS product.')
    return {'product': product_id, 'facts': product['facts']}


def resolve_components(components):
    """Resolve pinned records from disk. Workspace-supplied values are never used."""
    if not any(component.get('facts') for component in components):
        return {}, None
    products = catalog()
    resolved, context = {}, []
    for component in components:
        records = {fact['id']: fact for fact in products.get(component.get('product'), {}).get('facts', [])}
        facts = {}
        for binding in component.get('facts', []):
            fact = records.get(binding['fact'])
            message = None
            if fact is None:
                message = 'The selected record is unavailable for this product. Rebind it in the COTS pane.'
            elif fact['revision'] != binding['revision'] or fact['type'] != binding['type'] or fact['unit'] != binding['unit']:
                message = 'The catalogue record changed. Review and update its reference in the COTS pane.'
            result = {'state': 'pending' if message else 'value', 'value': None if message else fact['value'], 'message': message or ''}
            facts[binding['name']] = result
            context.append([component['key'], binding['name'], binding['fact'], binding['revision'], fact['revision'] if fact else None, result])
        resolved[component['key']] = facts
    return resolved, digest(sorted(context, key=lambda item: (item[0], item[1])))
