"""Validated Python catalog projected into JSON for the existing browser UI."""
import re

from catalog_data import ELEMENTS, REQUIREMENTS
from expressions import Evaluator
from models import Parameter, Requirement, Workspace


def catalog():
    elements = {element.model: element for element in ELEMENTS}
    if len(elements) != len(ELEMENTS):
        raise ValueError("Catalog element identifiers must be unique.")
    for element in ELEMENTS:
        if element.parent is not None and element.parent not in elements:
            raise ValueError(f"{element.model}: missing catalog parent {element.parent}.")
        for parameter in element.properties:
            parameter.validate()
        seen = set()
        parent = element
        while parent.parent is not None:
            if parent.model in seen:
                raise ValueError("Catalog element parents cannot form a cycle.")
            seen.add(parent.model)
            parent = elements[parent.parent]
    names = {requirement.name for requirement in REQUIREMENTS}
    if len(names) != len(REQUIREMENTS) or len({requirement.id for requirement in REQUIREMENTS}) != len(REQUIREMENTS):
        raise ValueError("Catalog requirement names and IDs must be unique.")
    units = {}
    for requirement in REQUIREMENTS:
        requirement.validate()
        for source in requirement.derives_from:
            if source not in names or source == requirement.name:
                raise ValueError(f"{requirement.name}: invalid derivation source {source}.")
        for parameter in requirement.parameters:
            if parameter.unit:
                if parameter.name in units and units[parameter.name] != parameter.unit:
                    raise ValueError(f"{parameter.name}: inconsistent catalog units.")
                units[parameter.name] = parameter.unit
    by_name = {requirement.name: requirement for requirement in REQUIREMENTS}
    parameter_types = {}
    for requirement in REQUIREMENTS:
        for parameter in requirement.parameters:
            previous = parameter_types.get(parameter.name)
            if previous is not None and previous != parameter.kind:
                raise ValueError(f'{parameter.name}: inconsistent catalog parameter types.')
            parameter_types[parameter.name] = parameter.kind
        seen, stack = set(), list(requirement.derives_from)
        while stack:
            name = stack.pop()
            if name == requirement.name:
                raise ValueError('Catalog derivation sources cannot form a cycle.')
            if name not in seen:
                seen.add(name)
                stack.extend(by_name[name].derives_from)
    rows = [Requirement(requirement.name, f'template_{requirement.name}', {}) for requirement in REQUIREMENTS]
    workspace = Workspace([Parameter(name, kind) for name, kind in parameter_types.items()], rows, [], [], {'modes': [], 'loads': [], 'links': []}, language='python')
    evaluator = Evaluator(workspace)
    for requirement, row in zip(REQUIREMENTS, rows):
        expressions = [(requirement.condition, 'boolean'), (requirement.acceptance, 'boolean')]
        expressions += [(parameter.expression, 'boolean' if parameter.kind == 'boolean' else 'number') for parameter in requirement.parameters if parameter.expression]
        for expression, expected in expressions:
            if not expression:
                continue
            for target, name in re.findall(r'@([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)', expression):
                if target not in by_name or name not in {parameter.name for parameter in by_name[target].parameters}:
                    raise ValueError(f'{requirement.name}: unknown template parameter {target}.{name}.')
            source = re.sub(r'@([A-Za-z_][A-Za-z0-9_]*)\.', r'template_\1.', expression)
            tree, _ = evaluator.tree(source)
            if evaluator.infer(tree, row) not in (expected, 'null'):
                raise ValueError(f'{requirement.name}: a catalog expression has an incompatible type.')
    projected = []
    for element in ELEMENTS:
        item = element.projection()
        context = "mission" if element.role == "orbit" else "eps" if element.role == "eps" else None
        requirements = [requirement.projection() for requirement in REQUIREMENTS if requirement.context == context]
        if requirements:
            item["requirements"] = requirements
        projected.append(item)
    return projected


def assess_requirement(identifier, values):
    requirement = next((item for item in REQUIREMENTS if identifier in (item.name, item.model, item.id)), None)
    if requirement is None:
        raise ValueError('Choose an existing Python requirement definition.')
    return requirement.assess(values)
