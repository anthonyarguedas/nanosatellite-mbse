"""Explicit restoration of incomplete statements without invented parameters."""

from .requirements import Requirement, Statement, _text


def _restore_text(statement, value):
    statement.draft_issues = ()
    try:
        Statement.text.fset(statement, value)
    except (ValueError, TypeError) as error:
        statement._text = _text(value, "Draft statement text")
        statement.draft_issues = (str(error),)
        statement._mark_changed()


class DraftStatement(Statement):
    """A saved incomplete statement that needs an engineer's edit."""

    text = property(Statement.text.fget, _restore_text)


class DraftRequirement(Requirement):
    """A saved incomplete requirement, preserving its original text and inputs."""

    text = property(Statement.text.fget, _restore_text)
