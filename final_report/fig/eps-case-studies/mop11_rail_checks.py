"""Replay the rail rows of the MOP-11 appendix: PYTHONPATH=. python3 <this file>."""

from decimal import Decimal as D
from hashlib import sha256
from pathlib import Path

from framework.cots import load_catalog
from framework.models import CubeSatBus, Mission, Property, VerificationCondition


# Query inputs are board requirements. Source conditions are selected by their
# physical meaning. Part numbers are used only to score the lists returned.
def setup(case, variant, catalogue):
    owner_type = 'RegulatorAndConverter' if case.endswith('reg') else 'PowerCircuit'
    mission = Mission()
    owner = getattr(mission.add(CubeSatBus('BUS')).EPS, owner_type)
    strict, missing = variant == 'strict', variant == 'missing'
    mode, kinds = '', {}

    def prop(name, unit):
        return owner.properties[name] if name in owner.properties else owner.define(name, Property(unit=unit))

    def check(name, unit, op, target):
        condition = VerificationCondition('check', prop(name, unit), Property(repr(target), unit), f'measure {op} target')
        owner.add_requirement(name + '_check', conditions=(condition,))

    if case.endswith('reg'):
        birds = case == 'BIRDS reg'
        check('minimum_input_voltage', 'V', '<=', 2.7 if birds else 6.0)
        check('maximum_input_voltage', 'V', '>=', (6.0 if strict else 4.2) if birds else (18 if strict else 8.4))
        check('configurable_output_voltage', '', 'is', birds)
        if birds:
            mode = 'electrical_characteristics_tj_minus40_to_125C'
            check('regulation_kind', '', '==', 'buck_boost')
            check('output_voltage_min', 'V', '<=', 3.3)
            check('output_voltage_max', 'V', '>=', 3.3)
        else:
            check('output_voltage', 'V', '==', 3.3)
        if missing:
            kinds['maximum_output_current'] = 'minimum'
            check('maximum_output_current', 'A', '>=', 2 if birds else 0.5)
    elif case == 'BIRDS switch':
        mode = 'enabled_ON_0V_I_grade'
        kinds['overcurrent_sense_voltage'] = 'typical'
        mission.define('shunt', Property(0.025, 'ohm'))
        prop('overcurrent_sense_voltage', 'V')
        owner.define('nominal_trip', Property('self.overcurrent_sense_voltage.value / self.mission.shunt.value', 'A'))
        check('input_voltage_min', 'V', '<=', 5.0)
        check('normal_input_voltage_max', 'V', '>=', 5.0)
        check('auto_retry', '', 'is', True)
        check('nominal_trip', 'A', '<=' if strict else '==', 1.5 if strict else 2.0)
        if missing:
            check('maximum_current', 'A', '>=', 2.0)  # Complete external switch path
    else:
        for edge, op in [('min', '<='), ('max', '>=')]:
            field = 'programmable_current_limit_' + edge
            kinds[field] = 'nominal'
            check(field, 'A', op, 2.1 if strict else 0.302)
        check('current_limit_programming_resistance_min', 'ohm', '<=', 3000)
        check('current_limit_programming_resistance_max', 'ohm', '>=', 3000)
        check('auto_retry', '', 'is', True)
        if missing:
            check('current_limit_programming_resistance', 'ohm', '==', 3000)
            check('current_limit', 'A', '>=', 0.302)

    conditions = [k for k, row in catalogue.conditions.items() if mode and row['operating_mode'] == mode
                  and (case != 'BIRDS switch' or (row['temperature_K'], row['input_voltage_V']) == ('298.15', '5'))]
    if case == 'OreSat switch' and missing:
        conditions = [k for k, rows in catalogue.condition_parameters.items() if any(
            r['parameter_name'] == 'current_limit_programming_resistance' and r['unit'] == 'ohm'
            and D(r['value']) == 3000 for r in rows)]
    if (mode and not conditions) or len(conditions) > 1:
        raise ValueError(f'Ambiguous source condition: {mode}')
    return owner, dict(condition_id=conditions[0] if conditions else '', value_kinds=kinds)


# Independent device references, in condition order, from the datasheets cited
# in the appendix. The second OreSat part belongs on a different branch.
REFERENCES = {
    'BIRDS reg': [('ti_tps63020qdsjtq1', [1.8, 5.5, True, 'buck_boost', 1.2, 5.5])],
    'OreSat reg': [('ti_tps62111rsat', [3.1, 17, False, 3.3]), ('ti_tps62112rsat', [3.1, 17, False, 5])],
    'BIRDS switch': [('adi_ltc4361idc_2_trmpbf', [2.5, 5.5, True, D('0.050') / D('0.025')])],
    'OreSat switch': [('ti_tps259621ddat', [0.125, 2, 453, 7869, True]),
                      ('ti_tps259620ddat', [0.125, 2, 453, 7869, False])],
}


def snapshot(mission, catalogue):
    model = [(o.path, type(o).__name__, getattr(o, 'expression', None), getattr(o, 'statement', None),
              [(n, p.expression, str(p.unit)) for n, p in o.properties.items()]) for o in mission.walk()]
    tables = (catalogue.products, catalogue.sources, catalogue.conditions, catalogue.condition_parameters,
              catalogue.curves, catalogue.elements)
    directory = Path(__file__).resolve().parents[3] / 'framework/cots'
    return (model, *(sha256(repr(t).encode()).digest() for t in tables),
            *(sha256(f.read_bytes()).digest() for f in sorted(directory.glob('*.tsv'))))


def run():
    catalogue = load_catalog()
    for case, parts in REFERENCES.items():
        for variant in ('baseline', 'strict', 'missing'):
            owner, selectors = setup(case, variant, catalogue)
            before = snapshot(owner.mission, catalogue)
            matches = owner.recommend_cots(**selectors)  # No candidate list or ranking
            assert before == snapshot(owner.mission, catalogue)
            for index, (part, ratings) in enumerate(parts if variant == 'baseline' else parts[:1]):
                expected = index == 0 and variant == 'baseline'
                match = next((m for m in matches if m.candidate.product_id == part and m.candidate.catalog_element == 'self'), None)
                assert (match is not None) == expected, (case, variant, part)
                if match:
                    assert match.candidate.catalog_condition == selectors['condition_id']
                    results = match.report.results
                else:  # The public query returns only matches. Diagnose exclusions in a fresh mission.
                    probe, _ = setup(case, variant, catalogue)
                    candidate = catalogue.product(part, model_class=type(owner), **selectors)
                    for n, p in candidate.properties.items():
                        if n in probe.properties:
                            setattr(probe, n, p.copy(None, n))
                        else:
                            probe.define(n, p.copy(None, n))
                    results = [r for req in probe.requirements for r in req.verify().results]
                actual = [(r.measure, r.value, r.status.value) for r in results]
                absent = (2 if case == 'OreSat switch' else 1) if variant == 'missing' else 0
                reference = ratings + [None] * absent
                assert len(actual) == len(reference)
                for (measure, _, status), rated in zip(actual, reference):
                    if rated is None:
                        assert measure is None and status == 'pending'
                    elif isinstance(rated, (bool, str)):
                        assert type(measure) is type(rated) and measure == rated and status == 'value'
                    else:
                        assert status == 'value' and abs(D(str(measure)) / D(str(rated)) - 1) <= D('0.01')
                verdicts = [v for _, v, _ in actual]
                expected_verdicts = [True] * len(reference)
                if variant == 'strict':
                    expected_verdicts[3 if case == 'BIRDS switch' else 1] = False
                elif absent:
                    expected_verdicts[-absent:] = [None] * absent
                elif index:
                    expected_verdicts[-1] = False
                assert verdicts == expected_verdicts, (case, variant, part, actual)
                print(case, variant, part, 'included' if match else 'excluded', actual)


if __name__ == '__main__':
    run()
