"""Body face identifiers and prescribed pointing choices."""

from enum import Enum


class Face(str, Enum):
    POS_X = "+X"
    NEG_X = "-X"
    POS_Y = "+Y"
    NEG_Y = "-Y"
    POS_Z = "+Z"
    NEG_Z = "-Z"

    @property
    def normal(self):
        sign = 1 if self.value[0] == "+" else -1
        return tuple(sign if axis == self.value[1] else 0 for axis in "XYZ")


class Pointing(str, Enum):
    SUN_POINTING = "sun_pointing"
    NADIR = "nadir"
