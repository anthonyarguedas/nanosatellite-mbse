"""EPS lifecycle behavior applied equally by a UI command or a REPL call."""

from ..elements import Subsystem
from ..database import DatabaseBacked


class EPS(Subsystem):
    model = "SpaceSegment::CubeSat::PowerSubsystem"
    default_name = "Power"
    id_prefix = "EPS"
    role = "eps"

    def initialize(self, session):
        if self.selection:
            return
        session.initialize_children(self)
        session.seed_requirements(self)
        for component in self.components:
            session.remember_component_defaults(component)

    def component_added(self, component, session):
        requirements = session.seed_component_requirements(component)
        if isinstance(component, DatabaseBacked):
            component.requirement_links = tuple(
                dict.fromkeys((*component.requirement_links, *requirements))
            )


class IntegratedEPS(EPS):
    default_name = "Integrated EPS"
