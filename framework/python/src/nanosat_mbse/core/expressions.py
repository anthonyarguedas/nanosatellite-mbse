"""Bounded Python expressions over a native evaluation context.

Only the explicitly handled syntax and functions run. This module uses neither
``eval`` nor ``exec`` and contains no workspace transport model.
"""

from __future__ import annotations

import ast
import io
import math
import operator
import statistics
import tokenize
from functools import lru_cache

from .verification import PendingValue


NUMERIC = {
    "sqrt": math.sqrt,
    "acos": math.acos,
    "arccos": math.acos,
    "floor": math.floor,
    "ceil": math.ceil,
    "abs": abs,
    "round": round,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "hypot": math.hypot,
}
AGGREGATES = {
    "sum": sum,
    "min": min,
    "max": max,
    "mean": statistics.mean,
    "median": statistics.median,
    "stdev": statistics.stdev,
    "pstdev": statistics.pstdev,
}
CONSTANTS = {
    "pi": math.pi,
    "math.pi": math.pi,
    "math.e": math.e,
    "math.tau": math.tau,
}
ARITY = {
    "sqrt": (1, 1),
    "acos": (1, 1),
    "arccos": (1, 1),
    "floor": (1, 1),
    "ceil": (1, 1),
    "abs": (1, 1),
    "round": (1, 2),
    "exp": (1, 1),
    "log": (1, 2),
    "log10": (1, 1),
    "sin": (1, 1),
    "cos": (1, 1),
    "tan": (1, 1),
    "hypot": (2, 32),
    "sum": (1, 1),
    "min": (1, 32),
    "max": (1, 32),
    "mean": (1, 1),
    "median": (1, 1),
    "stdev": (1, 1),
    "pstdev": (1, 1),
    "len": (1, 1),
    "range": (1, 3),
    "all": (1, 1),
    "any": (1, 1),
    "isclose": (2, 2),
    "isfinite": (1, 1),
    "all_assigned": (4, 4),
    "sum_assigned": (4, 4),
    "count_assigned": (1, 1),
}
BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
COMPARE = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


def qualify_names(source, references):
    """Qualify free parameter names while retaining formatting and local scopes."""
    if len(source) > 5000:
        return source
    try:
        tree = ast.parse(source.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError):
        return source
    prefix = len(source) - len(source.lstrip())
    lines = source.strip().splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    changes = []

    def position(line, column):
        return prefix + offsets[line - 1] + len(lines[line - 1].encode()[:column].decode())

    def visit(node, bound=frozenset()):
        if isinstance(node, ast.Name):
            if node.id in references and node.id not in bound:
                start = position(node.lineno, node.col_offset)
                end = position(node.end_lineno, node.end_col_offset)
                changes.append((start, end, references[node.id]))
        elif isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            nested = set(bound)
            for generator in node.generators:
                visit(generator.iter, nested)
                nested.update(item.id for item in ast.walk(generator.target) if isinstance(item, ast.Name))
                for condition in generator.ifs:
                    visit(condition, nested)
            visit(node.elt, nested)
        elif isinstance(node, ast.Call):
            for item in (*node.args, *(keyword.value for keyword in node.keywords)):
                visit(item, bound)
        elif not isinstance(node, ast.Attribute):
            for child in ast.iter_child_nodes(node):
                visit(child, bound)

    try:
        visit(tree)
    except RecursionError:
        return source
    for start, end, replacement in sorted(changes, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def rewrite_references(source, references):
    """Replace complete expression references, preserving strings and formatting."""
    if not isinstance(source, str) or len(source) > 5000:
        return source
    try:
        tree = ast.parse(source.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError):
        return source
    prefix = len(source) - len(source.lstrip())
    lines = source.strip().splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    changes = []

    def position(line, column):
        return prefix + offsets[line - 1] + len(lines[line - 1].encode()[:column].decode())

    def visit(node):
        name = symbol(node)
        if name in references:
            changes.append((position(node.lineno, node.col_offset),
                            position(node.end_lineno, node.end_col_offset), references[name]))
        else:
            for child in ast.iter_child_nodes(node):
                visit(child)

    try:
        visit(tree)
    except RecursionError:
        return source
    for start, end, value in sorted(changes, reverse=True):
        source = source[:start] + value + source[end:]
    return source


def finite_number(value):
    if type(value) not in (int, float):
        raise ValueError("This operation requires numeric operands.")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError("Arithmetic must produce a finite number.")
    return value


def symbol(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = symbol(node.value)
        if parent is not None:
            return f"{parent}.{node.attr}"
    return None


def function_name(node):
    name = symbol(node)
    if name and "." in name:
        namespace, name = name.rsplit(".", 1)
        if namespace not in ("math", "statistics"):
            return None
        if namespace == "statistics" and name not in (
            "mean",
            "median",
            "stdev",
            "pstdev",
        ):
            return None
        if namespace == "math" and name not in (
            "sqrt",
            "acos",
            "floor",
            "ceil",
            "exp",
            "log",
            "log10",
            "sin",
            "cos",
            "tan",
            "hypot",
            "isclose",
            "isfinite",
        ):
            return None
    return name if name in ARITY else None


@lru_cache(maxsize=256)
def parsed(source):
    if not isinstance(source, str) or len(source) > 5000:
        raise ValueError("Expressions can contain up to 5,000 characters.")
    try:
        tree = ast.parse(source.strip(), mode="eval").body
    except (SyntaxError, ValueError, RecursionError) as error:
        raise ValueError(
            f"Invalid Python expression: {getattr(error, 'msg', str(error))}"
        ) from None
    if any(
        token.type == tokenize.COMMENT
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
    ):
        raise ValueError(
            "Use the rationale field for comments. Expressions contain one calculation only."
        )
    stack, count = [(tree, 0)], 0
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > 2048 or depth > 64:
            raise ValueError(
                "The expression has too many tokens or is nested too deeply."
            )
        stack.extend((child, depth + 1) for child in ast.iter_child_nodes(node))
    return tree


class RestrictedPython:
    """An AST interpreter with names resolved by a native EvaluationContext."""

    def __init__(self, context, budget=None):
        self.context = context
        self.budget = [2_000_000] if budget is None else budget

    def tree(self, source):
        return parsed(source), source

    @staticmethod
    def require_type(actual, expected):
        if actual != expected:
            label = (
                "numeric"
                if expected == "number"
                else "Boolean"
                if expected == "boolean"
                else expected
            )
            raise ValueError(f"This operator requires {label} operands.")

    @staticmethod
    def assignment_arguments(node):
        if (
            len(node.args) != 4
            or any(not isinstance(item, ast.Constant) or type(item.value) is not str for item in node.args[:3])
            or not isinstance(node.args[3], ast.Name)
        ):
            raise ValueError(
                'Use all_assigned("Battery", "nominal_voltage", "==", target_voltage) '
                "or sum_assigned with an owned target parameter."
            )
        return (*[item.value for item in node.args[:3]], node.args[3].id)

    def infer(self, node, row, local=None):
        local = {} if local is None else local
        if isinstance(node, ast.Constant):
            if node.value is None:
                return "null"
            if type(node.value) is bool:
                return "boolean"
            if type(node.value) in (float, int):
                finite_number(node.value)
                return "number"
            if isinstance(node.value, str):
                return "string"
        name = symbol(node)
        if name and isinstance(node, (ast.Name, ast.Attribute)):
            if any(part.startswith("__") for part in name.split(".")):
                raise ValueError(
                    "Private names and attributes are unavailable in expressions."
                )
            if name in local:
                return local[name]
            if name in CONSTANTS:
                return "number"
            return self.context.reference_type(name, row)

        def kind(item):
            return self.infer(item, row, local)

        def require(item, expected):
            self.require_type(kind(item), expected)

        if isinstance(node, ast.IfExp):
            require(node.test, "boolean")
            left, right = kind(node.body), kind(node.orelse)
            if left != right and "null" not in (left, right):
                raise ValueError("Conditional branches must have the same type.")
            return right if left == "null" else left
        if isinstance(node, ast.UnaryOp) and type(node.op) in (
            ast.UAdd,
            ast.USub,
            ast.Not,
        ):
            expected = "boolean" if isinstance(node.op, ast.Not) else "number"
            require(node.operand, expected)
            return expected
        if isinstance(node, ast.BinOp) and type(node.op) in (*BINOPS, ast.Pow):
            require(node.left, "number")
            require(node.right, "number")
            return "number"
        if isinstance(node, ast.BoolOp) and type(node.op) in (ast.And, ast.Or):
            for item in node.values:
                require(item, "boolean")
            return "boolean"
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            for left, right, operation in zip(operands, operands[1:], node.ops):
                if type(operation) not in COMPARE:
                    raise ValueError("Unsupported Python comparison operator.")
                first, second = kind(left), kind(right)
                if isinstance(operation, (ast.Eq, ast.NotEq)):
                    if first != second:
                        raise ValueError("Equality operands must have the same type.")
                else:
                    self.require_type(first, "number")
                    self.require_type(second, "number")
                if symbol(left) == "mode" or symbol(right) == "mode":
                    literal = right if symbol(left) == "mode" else left
                    if (
                        isinstance(literal, ast.Constant)
                        and isinstance(literal.value, str)
                        and not any(
                            mode.name == literal.value
                            for mode in self.context.session.power.modes
                        )
                    ):
                        raise ValueError(f"Unknown spacecraft mode “{literal.value}”.")
            return "boolean"
        if isinstance(node, (ast.List, ast.Tuple)):
            if len(node.elts) > 1024:
                raise ValueError(
                    "Expression collections can contain up to 1,024 items."
                )
            types = {kind(item) for item in node.elts}
            if len(types) > 1:
                raise ValueError("Expression collections must have a common item type.")
            return "list:" + next(iter(types), "unknown")
        if (
            isinstance(node, (ast.ListComp, ast.GeneratorExp))
            and len(node.generators) == 1
        ):
            generator = node.generators[0]
            if (
                generator.is_async
                or not isinstance(generator.target, ast.Name)
                or generator.target.id.startswith("__")
            ):
                raise ValueError("Use a single named comprehension variable.")
            reserved = {
                *self.context.identifiers,
                *CONSTANTS,
                *ARITY,
                "mode",
                "math",
                "statistics",
            }
            if generator.target.id in reserved:
                raise ValueError(
                    "Comprehension variables must have their own local names."
                )
            element_type = kind(generator.iter)
            if not element_type.startswith("list:"):
                raise ValueError(
                    "Comprehensions require a bounded list, tuple or range."
                )
            nested = {**local, generator.target.id: element_type[5:]}
            for condition in generator.ifs:
                self.require_type(self.infer(condition, row, nested), "boolean")
            return "list:" + self.infer(node.elt, row, nested)
        if isinstance(node, ast.Call):
            name = function_name(node.func)
            if not name:
                raise ValueError(
                    "Unsupported Python function. Use registered scripts for unrestricted Python."
                )
            minimum, maximum = ARITY[name]
            if not minimum <= len(node.args) <= maximum:
                raise ValueError(
                    f"{name} requires {minimum}"
                    + (f" to {maximum}" if maximum != minimum else "")
                    + " argument(s)."
                )
            if name == "count_assigned":
                from .properties import resolve_property_type
                from .requirements import Requirement

                if not isinstance(row, Requirement):
                    raise TypeError("Assignment counts belong to a Requirement.")
                if not isinstance(node.args[0], ast.Constant) or type(node.args[0].value) is not str:
                    raise ValueError('Use count_assigned("Battery", cots_only=True).')
                resolve_property_type(node.args[0].value)
                for item in node.keywords:
                    if item.arg not in ("cots_only", "by_quantity"):
                        raise ValueError("Assignment counts accept cots_only and by_quantity only.")
                    require(item.value, "boolean")
                return "number"
            if name in ("all_assigned", "sum_assigned"):
                from .assignments import assignment_spec

                arguments = self.assignment_arguments(node)
                assignment_spec(row, *arguments, aggregate=name == "sum_assigned")
                for item in node.keywords:
                    if item.arg not in ("rel_tol", "abs_tol", "cots_only"):
                        raise ValueError("Assignment checks accept rel_tol, abs_tol and cots_only only.")
                    require(item.value, "boolean" if item.arg == "cots_only" else "number")
                return "boolean"
            if node.keywords and (
                name != "isclose"
                or any(item.arg not in ("rel_tol", "abs_tol") for item in node.keywords)
            ):
                raise ValueError("Unsupported function keyword arguments.")
            for item in node.keywords:
                require(item.value, "number")
            types = [kind(item) for item in node.args]
            if name in ("all", "any"):
                if types[0] not in ("list:boolean", "list:unknown"):
                    raise ValueError("all and any require Boolean collection items.")
            elif name in AGGREGATES or name == "len":
                if len(types) == 1 and types[0].startswith("list:"):
                    if name != "len" and types[0] not in (
                        "list:number",
                        "list:unknown",
                    ):
                        raise ValueError(
                            "This function requires numeric collection items."
                        )
                elif name not in ("min", "max"):
                    raise ValueError(
                        "This function requires a list, tuple or comprehension."
                    )
                else:
                    for item in types:
                        self.require_type(item, "number")
            else:
                for item in types:
                    self.require_type(item, "number")
            return (
                "list:number"
                if name == "range"
                else "boolean"
                if name in ("all", "any", "isclose", "isfinite")
                else "number"
            )
        raise ValueError(f"Unsupported Python syntax: {type(node).__name__}.")

    def evaluate(self, source, row, expected=None):
        tree = parsed(source)
        kind = self.infer(tree, row)
        if expected is not None and kind not in (expected, "null"):
            raise ValueError(f"The expression must produce a {expected}.")
        return self.visit(tree, row)

    def visit(self, node, row, local=None):
        self.budget[0] -= 1
        if self.budget[0] < 0:
            raise ValueError("The calculation exceeded its operation budget.")
        local = {} if local is None else local
        if isinstance(node, ast.Constant):
            if node.value is None:
                raise PendingValue("The expression is unset in this mode.")
            return node.value
        name = symbol(node)
        if isinstance(node, (ast.Name, ast.Attribute)) and name:
            if name in local:
                return local[name]
            if name in CONSTANTS:
                return CONSTANTS[name]
            return self.context.resolve_reference(name, row)

        def visit(item):
            return self.visit(item, row, local)

        if isinstance(node, ast.IfExp):
            return visit(node.body if visit(node.test) else node.orelse)
        if isinstance(node, ast.UnaryOp):
            value = visit(node.operand)
            return (
                not value
                if isinstance(node.op, ast.Not)
                else finite_number(-value if isinstance(node.op, ast.USub) else value)
            )
        if isinstance(node, ast.BoolOp):
            for item in node.values:
                value = visit(item)
                if (isinstance(node.op, ast.And) and not value) or (
                    isinstance(node.op, ast.Or) and value
                ):
                    return value
            return value
        if isinstance(node, ast.Compare):
            previous = visit(node.left)
            for operation, right in zip(node.ops, node.comparators):
                value = visit(right)
                if not COMPARE[type(operation)](previous, value):
                    return False
                previous = value
            return True
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow):
                if (
                    abs(left) > 1
                    and right > 0
                    and right * math.log(abs(left)) > 709.782712893384
                ):
                    raise ValueError("Power exceeds the finite numeric range.")
                return finite_number(left**right)
            return finite_number(BINOPS[type(node.op)](left, right))
        if isinstance(node, (ast.List, ast.Tuple)):
            return [visit(item) for item in node.elts]
        if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            generator = node.generators[0]

            def items():
                for item in visit(generator.iter):
                    nested = {**local, generator.target.id: item}
                    if all(
                        self.visit(condition, row, nested)
                        for condition in generator.ifs
                    ):
                        yield self.visit(node.elt, row, nested)

            return items() if isinstance(node, ast.GeneratorExp) else list(items())
        if isinstance(node, ast.Call):
            name = function_name(node.func)
            if name == "count_assigned":
                return self.context.count_assignments(
                    row, node.args[0].value,
                    **{item.arg: visit(item.value) for item in node.keywords},
                )
            if name in ("all_assigned", "sum_assigned"):
                return self.context.check_assignments(
                    row, name, *self.assignment_arguments(node),
                    **{item.arg: visit(item.value) for item in node.keywords},
                )
            args = [visit(item) for item in node.args]
            kwargs = {item.arg: visit(item.value) for item in node.keywords}
            if name == "range":
                if any(type(value) is not int for value in args):
                    raise ValueError("range requires Integer arguments.")
                values = range(*args)
                if len(values) > 1024:
                    raise ValueError("Expression ranges can contain up to 1,024 items.")
                return list(values)
            if name == "all":
                return all(args[0])
            if name == "any":
                return any(args[0])
            if name == "isclose":
                return math.isclose(*args, **kwargs)
            if name == "isfinite":
                return math.isfinite(args[0])
            if name == "len":
                return len(args[0])
            return finite_number(
                (NUMERIC.get(name) or AGGREGATES[name])(*args, **kwargs)
            )
        raise ValueError("Unsupported Python expression.")
