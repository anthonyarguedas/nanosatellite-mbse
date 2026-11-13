"""Native starter configuration, shared by the GUI and ordinary Python."""

from framework.models import CubeSatBus, Mission

mission = Mission()
bus = mission.add(CubeSatBus("BUS"))
