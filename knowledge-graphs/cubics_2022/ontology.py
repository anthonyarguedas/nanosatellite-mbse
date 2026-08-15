"""Small, source-aware ontology for the CUBICS 2022 knowledge graph.

The graph separates evidence-backed project facts from explicit public-evidence
gaps. Every node and edge carries a source URL.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True)
class Node:
    """A visual knowledge-graph entity with a primary provenance link."""

    id: str
    label: str
    title: str
    source_url: str
    color: str = field(default="#f5f5f5", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class GrantRecipient(Node):
    color: str = field(default="#f4a261", init=False)
    shape: str = field(default="box", init=False)


@dataclass(frozen=True, kw_only=True)
class CubeSat(Node):
    color: str = field(default="#4cc9f0", init=False)
    shape: str = field(default="triangle", init=False)


@dataclass(frozen=True, kw_only=True)
class Objective(Node):
    color: str = field(default="#90be6d", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class Payload(Node):
    color: str = field(default="#c77dff", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class Collaborator(Node):
    color: str = field(default="#ff9f1c", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class Partner(Node):
    color: str = field(default="#f7b267", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class Facility(Node):
    color: str = field(default="#43aa8b", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class Alias(Node):
    color: str = field(default="#adb5bd", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class EvidenceGap(Node):
    """An explicit, time-bounded absence in the reviewed public material."""

    color: str = field(default="#6c757d", init=False)
    shape: str = field(default="dot", init=False)


@dataclass(frozen=True, kw_only=True)
class Edge:
    """A directed, evidence-backed relation.

    ``evidence`` is rendered in the hover text.
    """

    id: str
    source_url: str
    label: str
    evidence: str = ""
    color: str = field(default="#d9d9d9a8", init=False)
    dashes: bool = field(default=False, init=False)


@dataclass(frozen=True, kw_only=True)
class Leads(Edge):
    label: str = field(default="leads", init=False)
    color: str = field(default="#f4a261cc", init=False)


@dataclass(frozen=True, kw_only=True)
class HasObjective(Edge):
    label: str = field(default="has objective", init=False)
    color: str = field(default="#90be6dcc", init=False)


@dataclass(frozen=True, kw_only=True)
class Carries(Edge):
    label: str = field(default="carries", init=False)
    color: str = field(default="#c77dffcc", init=False)


@dataclass(frozen=True, kw_only=True)
class CollaboratesWith(Edge):
    label: str = field(default="collaborates with", init=False)
    color: str = field(default="#ff9f1ccc", init=False)


@dataclass(frozen=True, kw_only=True)
class PartnersWith(Edge):
    label: str = field(default="partners with", init=False)
    color: str = field(default="#f7b267cc", init=False)


@dataclass(frozen=True, kw_only=True)
class UsesFacility(Edge):
    label: str = field(default="uses / tests at", init=False)
    color: str = field(default="#43aa8bcc", init=False)


@dataclass(frozen=True, kw_only=True)
class RenamedTo(Edge):
    label: str = field(default="renamed to", init=False)
    color: str = field(default="#adb5bdcc", init=False)
    dashes: bool = field(default=True, init=False)


@dataclass(frozen=True, kw_only=True)
class NotPubliclyDocumented(Edge):
    label: str = field(default="not publicly documented", init=False)
    color: str = field(default="#6c757dcc", init=False)
    dashes: bool = field(default=True, init=False)


@dataclass(frozen=True, kw_only=True)
class PossiblySameAs(Edge):
    """A source-supported but unresolved historical project-name mapping."""

    label: str = field(default="possibly same project as", init=False)
    color: str = field(default="#adb5bdcc", init=False)
    dashes: bool = field(default=True, init=False)


@dataclass(frozen=True)
class RelationRecord:
    source: str
    target: str
    edge: Edge
