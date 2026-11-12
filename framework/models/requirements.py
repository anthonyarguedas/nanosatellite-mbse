"""Boolean conditions, separate evaluation status and transitive failure traces."""

from dataclasses import dataclass

from .objects import ModelObject
from .properties import EvaluationContext, EvaluationStatus, PendingValue, Property
from .properties import expression as expression_source


@dataclass(frozen=True)
class VerificationFailure:
    requirement: object
    condition: object
    path: tuple
    measure: object
    target: object

    @property
    def instance(self):
        return self.path[-1].owner

    def explain(self):
        path = " -> ".join(prop.reference for prop in self.path)
        return f"{self.condition.path}: {self.condition.expression} failed (measure={self.measure!r}, target={self.target!r}) via {path}"


@dataclass(frozen=True)
class ConditionResult:
    condition: object
    status: EvaluationStatus
    value: object = None
    measure: object = None
    target: object = None
    paths: tuple = ()
    message: str = ""

    @property
    def requirement(self):
        return self.condition.parent

    @property
    def failures(self):
        if self.value is not False or self.status is not EvaluationStatus.VALUE:
            return ()
        return tuple(VerificationFailure(self.requirement, self.condition, path, self.measure, self.target) for path in self.paths)


@dataclass(frozen=True)
class InstanceVerification:
    instance: object
    results: tuple

    @property
    def verified(self):
        if any(result.value is False for result in self.results):
            return False
        if self.results and all(result.value is True for result in self.results):
            return True
        return None

    @property
    def status(self):
        if any(result.status is EvaluationStatus.ERROR for result in self.results):
            return EvaluationStatus.ERROR
        if not self.results or any(result.status is EvaluationStatus.PENDING for result in self.results):
            return EvaluationStatus.PENDING
        return EvaluationStatus.VALUE

    @property
    def failures(self):
        return tuple(failure for result in self.results for failure in result.failures if failure.instance is self.instance or failure.path[-1] is self.instance)


@dataclass(frozen=True)
class VerificationReport:
    mission: object
    results: tuple

    def for_instance(self, instance):
        if isinstance(instance, str):
            instance = self.mission.get(instance)
        related = tuple(result for result in self.results if any(path[-1].owner is instance or path[-1] is instance for path in result.paths))
        return InstanceVerification(instance, related)

    @property
    def verified(self):
        return InstanceVerification(self.mission, self.results).verified

    @property
    def status(self):
        return InstanceVerification(self.mission, self.results).status

    @property
    def failures(self):
        return tuple(failure for result in self.results for failure in result.failures)


class VerificationCondition(ModelObject):
    measure = Property()
    target = Property()

    def __init__(self, name, measure, target, expression):
        super().__init__(name, measure=measure, target=target)
        self.expression = expression

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, source):
        source = expression_source(source)
        if source is None:
            raise ValueError("Supply a boolean Python expression.")
        self._expression = source

    def evaluate(self, *, mode=None):
        context = EvaluationContext(self.mission, mode)
        measure, target, value, message, paths = None, None, None, "", ()
        with context:
            try:
                try:
                    measure = context.read(self.measure)
                finally:
                    paths = context.paths(self.measure)
                target = context.read(self.target)
                value = context.execute(self.expression, self, measure=measure, target=target)
                if type(value) is not bool:
                    raise TypeError("A VerificationCondition must return a boolean.")
                status = EvaluationStatus.VALUE
            except PendingValue as error:
                status, value, message = EvaluationStatus.PENDING, None, str(error)
            except Exception as error:
                status, value, message = EvaluationStatus.ERROR, None, f"{type(error).__name__}: {error}"
        return ConditionResult(self, status, value, measure, target, paths, message)


class Requirement(ModelObject):
    def __init__(self, name, *, statement="", rationale="", text=None, conditions=(), **bindings):
        if text is not None:
            if statement:
                raise TypeError("Specify statement or its text alias, not both.")
            statement = text
        if not isinstance(statement, str) or not isinstance(rationale, str):
            raise TypeError("Statement and rationale are text.")
        super().__init__(name, **bindings)
        self.statement = statement
        self.rationale = rationale
        for condition in conditions:
            self.add(condition)

    @property
    def text(self):
        """Compatibility alias for the statement template."""
        return self.statement

    @text.setter
    def text(self, value):
        self.statement = value

    def render_statement(self, *, mode=None):
        """Render prose independently of verification, using owned condition names."""
        fields = {condition.name: condition for condition in self.conditions}
        fields.update(self=self, mode=mode)
        with EvaluationContext(self.mission, mode):
            return self.statement.format_map(fields)

    @property
    def conditions(self):
        return self.children

    def accepts(self, child):
        return isinstance(child, VerificationCondition)

    def verify(self, *, mode=None):
        return VerificationReport(self.mission, tuple(condition.evaluate(mode=mode) for condition in self.conditions))

    @property
    def verification(self):
        return self.verify()
