# %% Imports

from __future__ import annotations


# %% Nodes

class Node:
    def __init__(self, id: str, label: str, title: str, source_url: str):
        self.id = id
        self.label = label  # Short
        self.title = title  # Long, shown on hover
        self.source_url = source_url
        self.color = "#ffffff"  # HTML/CSS color
        self.shape = "dot"


class Agency(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = "yellow"


class University(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = "yellow"


class Company(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = "yellow"


class Service(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = "orange"


class Mission(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = "orange"


class Constellation(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shape = "star"


class Payload(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shape = "square"


class Spacecraft(Node):
    def __init__(self, is_early_failure: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.shape = "triangleDown" if is_early_failure else "dot"


# %% Edges

class Edge:
    def __init__(self, id: str, source_url: str, status: str = "unknown"):
        self.id = id
        self.source_url = source_url

        match status:
            case "present":
                self.color = "#ffffffa0"
                self.status = "present"
            case "past":
                self.color = "#ffffff40"
                self.status = "past"
            case "future":
                self.color = "#ffffff60"
                self.status = "future"
            case "unknown":
                self.color = "#ffffff80"
                self.status = "unknown"
            case _:
                raise ValueError(
                    "status must be one of: 'present', 'past', 'future', 'unknown'"
                )


# An agency, university, or company can launch a spacecraft or constellation
class Launches(Edge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "launches"
            case "past":
                self.label = "launched"
            case "future":
                self.label = "will launch"
            case "unknown":
                self.label = "has launched"


# An agency, university, or company can operate a spacecraft, constellation,
# mission, or service
class Operates(Edge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "operates"
            case "past":
                self.label = "operated"
            case "future":
                self.label = "will operate"
            case "unknown":
                self.label = "has operated"


# A mission or service can use a spacecraft or constellation
class Uses(Edge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "uses"
            case "past":
                self.label = "used"
            case "future":
                self.label = "will use"
            case "unknown":
                self.label = "has used"


# A spacecraft can contain a payload; a constellation can contain a spacecraft
class Contains(Edge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "contains"
            case "past":
                self.label = "contained"
            case "future":
                self.label = "will contain"
            case "unknown":
                self.label = "has contained"


class Funds(Edge):
    def __init__(self, completed: bool = False, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "funds"
            case "past":
                self.label = "funded"
            case "future":
                self.label = "will fund"
            case "unknown":
                self.label = "has funded"


class Commissions(Edge):
    def __init__(self, completed: bool = False, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "commissions"
            case "past":
                self.label = "commissioned"
            case "future":
                self.label = "will commission"
            case "unknown":
                self.label = "has commissioned"


# An agency, a university, or a company can develop a mission, a spacecraft,
# a constellation, or a payload. A developer might not operate; operating
# comes after developing.
class Develops(Edge):
    def __init__(self, completed: bool = False, **kwargs):
        super().__init__(**kwargs)

        match self.status:
            case "present":
                self.label = "develops"
            case "past":
                self.label = "developed"
            case "future":
                self.label = "will develop"
            case "unknown":
                self.label = "has developed"