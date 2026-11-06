"""Requirement checks and script input projections evaluated in Python."""
from __future__ import annotations

import ast

from expressions import Evaluator, symbol
from models import Pending, Workspace


PRIORITY = ("error", "fail", "pending", "unset", "pass", "varying", "value")


def state_of(results):
    return next((state for state in PRIORITY if any(result["state"] == state for result in results)), "unset")


def branches(evaluator, source):
    """Return a UI projection of a mode conditional without evaluating branches."""
    try:
        tree, text = evaluator.tree(source)
        modes = evaluator.workspace.modes

        def guard(node):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1 or type(node.ops[0]) not in (ast.Eq, ast.NotEq):
                return None
            left, right = node.left, node.comparators[0]
            literal = right if symbol(left) == "mode" else left if symbol(right) == "mode" else None
            if not isinstance(literal, ast.Constant) or not isinstance(literal.value, str):
                return None
            mode = next((mode for mode in modes if mode["name"] == literal.value), None)
            return (mode, isinstance(node.ops[0], ast.Eq)) if mode else None

        first = guard(tree.test) if isinstance(tree, ast.IfExp) else None
        if not first:
            return None

        def branch(node, mode):
            condition = guard(node.test) if isinstance(node, ast.IfExp) else None
            if condition:
                selected = (condition[0]["key"] == mode["key"]) == condition[1]
                return branch(node.body if selected else node.orelse, mode)
            if isinstance(node, ast.Constant) and node.value is None:
                return None
            return ast.get_source_segment(text, node)

        return {"values": {mode["key"]: branch(tree, mode) for mode in modes}, "lastEdited": first[0]["key"]}
    except (ValueError, SyntaxError, TypeError):
        return None


def parameter_result(evaluator, row, name):
    raw = row.parameters.get(name)
    if raw is None or isinstance(raw, str) and not raw.strip():
        return {"state": "unset", "value": None, "message": "No Python parameter expression."}
    try:
        value = evaluator.parameter(row, name)
        return {"state": "value", "value": value, "message": f"= {value}"}
    except (ValueError, ArithmeticError, TypeError) as error:
        return {"state": "pending" if isinstance(error, Pending) else "error", "value": None, "message": str(error)[:300]}


def compute(workspace, mode, budget):
    evaluator = Evaluator(workspace, mode, budget)
    results = []
    for row in workspace.requirements:
        parameters = {parameter.name: parameter_result(evaluator, row, parameter.name) for parameter in workspace.variables}
        methods = []
        for method in row.methods:
            try:
                if method.get("script"):
                    evaluator.script(method["script"])
                if not method["condition"].strip():
                    methods.append({"key": method["key"], "state": "pending", "message": "Enter a Python condition for this verification method."})
                    continue
                value = evaluator.expression(method["condition"], row)
                methods.append({"key": method["key"], "state": "pass" if value else "fail", "message": method["condition"]})
            except (ValueError, ArithmeticError, TypeError) as error:
                methods.append({"key": method["key"], "state": "pending" if isinstance(error, Pending) else "error", "message": str(error)[:300]})
        results.append({"key": row.key, "parameters": parameters, "values": {name: result["value"] for name, result in parameters.items()},
                        "methods": methods, "state": state_of(methods),
                        "message": "\n".join(result["message"] for result in methods) if methods else "No verification condition. Add a Python condition to verify this row."})
    scripts = []
    for script in workspace.scripts:
        parameters = {parameter.name: parameter_result(evaluator, script, parameter.name) for parameter in script.inputs}
        scripts.append({"key": script.key, "parameters": parameters, "values": {name: result["value"] for name, result in parameters.items()}})
    return results, scripts


def aggregate(results, modes, methods=False):
    def describe(items):
        return "\n".join(f"{mode['name']}: {item.get('message', '')}" for mode, item in zip(modes, items))
    parameters = {}
    for name in results[0]["parameters"]:
        cells = [result["parameters"][name] for result in results]
        same = all(cell["state"] == "value" and cell["value"] == cells[0]["value"] for cell in cells)
        parameters[name] = cells[0] if same else {"state": "varying" if all(cell["state"] == "value" for cell in cells) else state_of(cells), "value": None, "message": describe(cells)}
    combined = {"key": results[0]["key"], "parameters": parameters, "values": {name: cell["value"] for name, cell in parameters.items()},
                "modes": [{"mode": mode["key"], **result} for mode, result in zip(modes, results)]}
    if methods:
        combined.update(state=state_of(results), message=describe(results), methods=[])
        for index, method in enumerate(results[0]["methods"]):
            cells = [result["methods"][index] for result in results]
            combined["methods"].append({"key": method["key"], "state": state_of(cells), "message": describe(cells),
                                        "modes": [{"mode": mode["key"], **cell} for mode, cell in zip(modes, cells)]})
    return combined


def evaluate(request):
    workspace = Workspace.read(request.get("workspace"), request.get("runs"))
    budget = [2000000]
    modes = workspace.modes
    if "mode" in request:
        selected = request["mode"]
        if selected is not None and not any(mode["key"] == selected for mode in modes):
            raise ValueError("Choose an existing spacecraft mode.")
        results, scripts = compute(workspace, selected, budget)
    elif modes:
        batches = [compute(workspace, mode["key"], budget) for mode in modes]
        results = [aggregate([batch[0][index] for batch in batches], modes, True) for index in range(len(workspace.requirements))]
        scripts = [aggregate([batch[1][index] for batch in batches], modes) for index in range(len(workspace.scripts))]
    else:
        results, scripts = compute(workspace, None, budget)
    metadata = Evaluator(workspace, budget=budget)
    for row, result in zip(workspace.requirements, results):
        for name, source in row.parameters.items():
            if source and name in result["parameters"]:
                projection = branches(metadata, source)
                if projection:
                    result["parameters"][name]["branches"] = projection
                    result["parameters"][name]["expressionSource"] = source
    return {"results": results, "scripts": scripts, "engine": "python"}


def script_inputs(request):
    workspace = Workspace.read(request.get("workspace"), request.get("runs"))
    script = next((script for script in workspace.scripts if script.key == request.get("script")), None)
    if script is None:
        raise ValueError("Choose an existing Python script instance.")
    evaluator = Evaluator(workspace, request.get("mode"))
    inputs = {parameter.name: evaluator.parameter(script, parameter.name) for parameter in script.inputs}
    requirements = {row.id: {parameter.name: parameter_result(evaluator, row, parameter.name)["value"] for parameter in workspace.variables}
                    for row in workspace.requirements}
    return {"inputs": inputs, "requirements": requirements}
