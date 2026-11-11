"""Requirement predicates and their transient results.

Analysis script execution uses its own interface. A predicate checks values
that are already available and never records a successful analysis execution.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping, Optional, Tuple, Union

from .identity import Identified
from uuid import uuid4


Scalar = Union[int, float, bool, str]


@dataclass(frozen=True)
class DraftExpression:
    """Retained invalid source, which remains editable and never executes."""

    source: str
    error: str


Expression = Union[
    str, DraftExpression, Callable[[Mapping[str, Scalar]], Optional[Scalar]]
]


def restored_expression(source: str) -> Expression:
    """Preserve a saved draft without weakening normal constructor validation."""
    try:
        validate_expression(source)
    except (SyntaxError, ValueError) as error:
        return DraftExpression(source, str(error))
    return source


class PendingValue(ValueError):
    """A required input or execution result is unavailable.

    script_key identifies a dependency for an explicit verification runner.
    """

    def __init__(self, message, script_key=None):
        super().__init__(message)
        self.script_key = script_key


class VerificationState(str, Enum):
    UNSET = "unset"
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


def validate_expression(expression: Expression) -> None:
    """Check syntax without executing source or importing a calculation engine."""
    if isinstance(expression, DraftExpression):
        if not isinstance(expression.source, str):
            raise TypeError("Draft expression source must be text.")
    elif isinstance(expression, str):
        if not expression.strip():
            raise ValueError("An expression must contain Python source.")
        if len(expression) > 5000:
            raise ValueError("Expressions can contain up to 5,000 characters.")
        try:
            tree = ast.parse(expression.strip(), mode="eval").body
        except RecursionError:
            raise ValueError("The expression is nested too deeply.") from None
        stack, count = [(tree, 0)], 0
        while stack:
            node, depth = stack.pop()
            count += 1
            if count > 2048 or depth > 64:
                raise ValueError(
                    "The expression has too many tokens or is nested too deeply."
                )
            stack.extend((child, depth + 1) for child in ast.iter_child_nodes(node))
    elif not callable(expression):
        raise TypeError("An expression must be Python source or a callable.")


@dataclass(frozen=True)
class MethodResult:
    name: str
    state: VerificationState
    message: str = ""


@dataclass(frozen=True)
class VerificationResult:
    """A fresh assessment, kept separate from requirement configuration."""

    methods: Tuple[MethodResult, ...] = ()
    # Native ModeVerification records are supplied for aggregate assessments.
    modes: Tuple[object, ...] = ()

    @property
    def state(self) -> VerificationState:
        if not self.methods:
            return VerificationState.UNSET
        for state in (
            VerificationState.ERROR,
            VerificationState.FAIL,
            VerificationState.PENDING,
            VerificationState.UNSET,
        ):
            if any(method.state == state for method in self.methods):
                return state
        return VerificationState.PASS

    @property
    def verified(self) -> bool:
        return self.state == VerificationState.PASS


@dataclass(frozen=True)
class VerificationMethod:
    """A Boolean condition, expressed as Python source or a trusted function.

    A native function receives a lazy mapping of this requirement's parameters.
    Reading an unset parameter raises PendingValue. Expression source requires
    an evaluator supplied by the caller.
    """

    name: str
    condition: Expression
    key: str = field(default_factory=lambda: str(uuid4()))
    source: Optional[Identified] = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Name each verification method.")
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("A verification method needs a stable key.")
        validate_expression(self.condition)

    def evaluate(
        self,
        values: Mapping[str, Scalar],
        evaluate_expression: Optional[Callable[[str], Optional[Scalar]]] = None,
        source_ready: Optional[Callable[[Identified], bool]] = None,
    ) -> MethodResult:
        try:
            if self.source is not None and (
                source_ready is None or not source_ready(self.source)
            ):
                raise PendingValue(
                    "Current evidence is required for the selected verification source."
                )
            if isinstance(self.condition, DraftExpression):
                if not self.condition.source.strip():
                    raise PendingValue("Enter a verification condition.")
                raise ValueError(self.condition.error)
            if isinstance(self.condition, str):
                if evaluate_expression is None:
                    raise PendingValue(
                        "Provide an evaluator for Python expression source."
                    )
                value = evaluate_expression(self.condition)
            else:
                value = self.condition(values)
            if value is None:
                raise PendingValue("The verification condition has no result yet.")
            if type(value) is not bool:
                raise TypeError("A verification condition must return a Boolean.")
            state = VerificationState.PASS if value else VerificationState.FAIL
            return MethodResult(self.name, state)
        except PendingValue as error:
            return MethodResult(self.name, VerificationState.PENDING, str(error))
        except Exception as error:
            return MethodResult(
                self.name, VerificationState.ERROR, f"{type(error).__name__}: {error}"
            )
