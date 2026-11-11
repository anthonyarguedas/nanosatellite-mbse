"""Spacecraft mode references and identity-preserving mode operations."""

from __future__ import annotations

import ast
import io
import json
import tokenize


def _offsets(lines):
    result = [0]
    for line in lines:
        result.append(result[-1] + len(line))
    return result


def _draft_references(source, name):
    """Retain mode links even while an expression is an incomplete draft."""
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type not in (
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.COMMENT,
            ):
                tokens.append(token)
    except (tokenize.TokenError, IndentationError):
        pass
    offsets = _offsets(source.splitlines(keepends=True))
    spans = set()
    for first, operation, last in zip(tokens, tokens[1:], tokens[2:]):
        literal = (
            last
            if first.type == tokenize.NAME and first.string == "mode"
            else first
            if last.type == tokenize.NAME and last.string == "mode"
            else None
        )
        if (
            operation.string not in ("==", "!=")
            or literal is None
            or literal.type != tokenize.STRING
        ):
            continue
        try:
            value = ast.literal_eval(literal.string)
        except (SyntaxError, ValueError):
            continue
        if value == name:
            spans.add(
                (
                    offsets[literal.start[0] - 1] + literal.start[1],
                    offsets[literal.end[0] - 1] + literal.end[1],
                )
            )
    return tuple(sorted(spans))


def _references(source, name):
    if not isinstance(source, str):
        return ()
    normalized = source.strip()
    try:
        tree = ast.parse(normalized, mode="eval")
    except (ValueError, SyntaxError):
        return _draft_references(source, name)
    prefix = len(source) - len(source.lstrip())
    lines = normalized.splitlines(keepends=True)
    offsets = _offsets(lines)

    def position(line, column):
        # AST columns are UTF-8 bytes. Python string slices use characters.
        return (
            prefix
            + offsets[line - 1]
            + len(lines[line - 1].encode("utf-8")[:column].decode("utf-8"))
        )

    selected = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        for left, right in zip(operands, operands[1:]):
            literal = (
                right
                if isinstance(left, ast.Name) and left.id == "mode"
                else left
                if isinstance(right, ast.Name) and right.id == "mode"
                else None
            )
            if isinstance(literal, ast.Constant) and literal.value == name:
                selected.add(
                    (
                        position(literal.lineno, literal.col_offset),
                        position(literal.end_lineno, literal.end_col_offset),
                    )
                )
    return tuple(sorted(selected))


def mode_referenced(source, name):
    return bool(_references(source, name))


def rewrite_mode(source, old_name, new_name):
    spans = _references(source, old_name)
    if not spans:
        return source
    replacement = json.dumps(new_name, ensure_ascii=False)
    for start, end in reversed(spans):
        source = source[:start] + replacement + source[end:]
    return source


def configure_parameter_states(
    session, target, parameter, *, values=None, last_edited=None, merge=False
):
    """Bind per-mode editor inputs using the same native rule in UI and REPL."""
    from dataclasses import replace
    from .session import expression_source
    from .predicates import restored_expression
    from .evaluation import branches

    if type(merge) is not bool:
        raise ValueError("Parameter state merge is a Boolean choice.")
    row = session.get(target)
    binding = row.parameters[parameter]
    if callable(binding.expression):
        raise ValueError("Native callable parameters retain their Python binding.")
    modes = tuple(session.power.modes)
    if not modes:
        raise ValueError("Define a spacecraft mode before splitting a parameter.")
    keys = {mode.key for mode in modes}
    source = expression_source(binding)
    existing = branches(session.evaluation_context(), source) if source else None
    if values is None:
        values = (
            existing["values"] if existing else {mode.key: source for mode in modes}
        )
    if not isinstance(values, dict) or set(values) - keys:
        raise ValueError("State expressions must reference configured modes.")
    if any(
        value is not None
        and (
            not isinstance(value, str)
            or len(value) > 5000
            or "\n" in value
            or "\r" in value
        )
        for value in values.values()
    ):
        raise ValueError("Enter one Python expression per state row.")
    selected = (
        session.resolve_mode(last_edited).key
        if last_edited is not None
        else (existing["lastEdited"] if existing else modes[0].key)
    )
    if selected not in keys:
        raise ValueError("Select a configured state for the parameter.")
    if merge:
        source = values.get(selected)
    else:
        ordered = sorted(modes, key=lambda mode: mode.key != selected)
        source = "None"
        for mode in reversed(ordered):
            value = values.get(mode.key)
            source = f"({value if value and value.strip() else 'None'}) if mode == {json.dumps(mode.name, ensure_ascii=False)} else {source}"
    result = replace(
        binding,
        value=None,
        expression=None if source is None else restored_expression(source),
    )
    session.configure_parameter(row, result)
    return result
