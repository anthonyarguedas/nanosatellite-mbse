"""Medium activity atmospheric drag applied to the live orbital spacecraft.

Density uses the same annual and orbital mean NRLMSISE-00 table as the lifetime
screening model. Forces use each hub's actual position and velocity relative to
co-rotating air. Mean projected areas are held constant. Drag torque is omitted.
"""

import numpy as np
from numba import njit

from orbit_environment import EARTH_RADIUS_M, EARTH_SPIN_RAD_S


@njit(cache=True)
def drag_forces(states, heights, log_density, coefficient_area):
    forces = np.zeros((2, 3))
    power, density_sum = 0.0, 0.0
    for bus in range(2):
        x, y, z = states[bus, :3]
        altitude = np.sqrt(x * x + y * y + z * z) - EARTH_RADIUS_M
        density = np.exp(np.interp(altitude, heights, log_density))
        relative = np.array(
            [
                states[bus, 3] + EARTH_SPIN_RAD_S * y,
                states[bus, 4] - EARTH_SPIN_RAD_S * x,
                states[bus, 5],
            ]
        )
        scale = -0.5 * coefficient_area * density * np.linalg.norm(relative)
        for axis in range(3):
            forces[bus, axis] = scale * relative[axis]
            power += forces[bus, axis] * states[bus, 3 + axis]
        density_sum += density
    return forces, power, density_sum / 2


class MediumDrag:
    def __init__(self, heights, densities, pair_area_m2, coefficient=2.2):
        self.heights = np.asarray(heights, dtype=float)
        densities = np.asarray(densities, dtype=float)
        if (
            len(self.heights) < 2
            or len(self.heights) != len(densities)
            or not np.all(np.isfinite(self.heights))
            or np.any(np.diff(self.heights) <= 0)
            or not np.all(np.isfinite(densities))
            or np.any(densities <= 0)
        ):
            raise ValueError("Drag density table must be positive, finite and ordered")
        self.log_density = np.log(densities)
        if not np.isfinite(pair_area_m2) or pair_area_m2 <= 0:
            raise ValueError("Mean pair area must be finite and positive")
        if not np.isfinite(coefficient) or coefficient < 0:
            raise ValueError("Drag coefficient must be finite and nonnegative")
        self.pair_area_m2, self.coefficient = pair_area_m2, coefficient
        self.work_j, self.power_w, self.mean_density_kg_m3 = 0.0, 0.0, 0.0
        self.last_time = None

    @classmethod
    def from_orbit(cls, config, orbit, coefficient=2.2):
        from lifetime import MEDIUM_ACTIVITY, build_atmosphere_table, tumbling_pair_area

        print("Building the medium activity NRLMSISE-00 density table...", flush=True)
        table = build_atmosphere_table(orbit, MEDIUM_ACTIVITY)
        return cls(
            table.altitude_m,
            table.density_kg_m3,
            tumbling_pair_area(config),
            coefficient,
        )

    def forces(self, states, time):
        if self.last_time is not None and time < self.last_time:
            raise ValueError("Drag integration time must increase")
        force, power, density = drag_forces(
            states,
            self.heights,
            self.log_density,
            self.coefficient * self.pair_area_m2 / 2,
        )
        if self.last_time is not None:
            self.work_j += 0.5 * (power + self.power_w) * (time - self.last_time)
        self.last_time, self.power_w, self.mean_density_kg_m3 = time, power, density
        return force

    def summary(self):
        return {
            "model": "Native NRLMSISE-00 annual and orbit averaged density table",
            "solar_activity": "medium",
            "f107_sfu": 140.0,
            "ap": 10.0,
            "coefficient": self.coefficient,
            "mean_pair_area_m2": self.pair_area_m2,
            "air_co_rotation": True,
            "drag_work_j": float(self.work_j),
            "force_application": "Individual hub centers, using their actual velocities",
            "assumptions": [
                "Fixed mean projected area, split equally between the two buses.",
                "Medium activity is a screening assumption, not a space weather forecast.",
                "Density is averaged over seasons and local solar times. Winds and drag torque are omitted.",
            ],
        }
