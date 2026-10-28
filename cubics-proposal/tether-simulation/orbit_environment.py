"""Earth J2 gravity and a first order circular Sun synchronous orbit design."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import numpy as np
from Basilisk.simulation import (
    gravityEffector,
    spacecraft,
    sphericalHarmonicsGravityModel,
)
from Basilisk.utilities import SimulationBaseClass, macros, orbitalMotion

EARTH_MU = 3.986004418e14
EARTH_RADIUS_M = 6378137.0
EARTH_J2 = 1.08262668e-3
EARTH_SPIN_RAD_S = 7.2921150e-5
TROPICAL_YEAR_S = 365.2422 * 86400.0


@dataclass(frozen=True)
class OrbitConfig:
    altitude_m: float = 600000.0
    raan_deg: float = 0.0
    epoch_utc: str = "2026-01-01T00:00:00Z"

    @property
    def radius_m(self):
        return EARTH_RADIUS_M + self.altitude_m

    @property
    def mean_motion_rad_s(self):
        return np.sqrt(EARTH_MU / self.radius_m**3)

    @property
    def period_s(self):
        return 2 * np.pi / self.mean_motion_rad_s

    @property
    def inclination_rad(self):
        rate = 2 * np.pi / TROPICAL_YEAR_S
        factor = (
            1.5
            * EARTH_J2
            * self.mean_motion_rad_s
            * (EARTH_RADIUS_M / self.radius_m) ** 2
        )
        cosine = -rate / factor
        if abs(cosine) > 1:
            raise ValueError("No circular J2 Sun synchronous solution at this altitude")
        return np.arccos(cosine)

    @property
    def epoch(self):
        value = datetime.fromisoformat(self.epoch_utc.replace("Z", "+00:00"))
        if value.tzinfo is None:
            raise ValueError("The epoch needs a UTC offset or Z")
        return value.astimezone(timezone.utc)

    def validate(self):
        if not np.isfinite(self.altitude_m) or self.altitude_m <= 0:
            raise ValueError("Orbital altitude must be positive")
        if not np.isfinite(self.raan_deg):
            raise ValueError("RAAN must be finite")
        _ = self.inclination_rad, self.epoch

    def initial_state(self):
        self.validate()
        oe = orbitalMotion.ClassicElements()
        oe.a, oe.e = self.radius_m, 0.0
        oe.i, oe.Omega = self.inclination_rad, np.deg2rad(self.raan_deg)
        oe.omega, oe.f = 0.0, 0.0
        return orbitalMotion.elem2rv(EARTH_MU, oe)

    def summary(self):
        return {
            **asdict(self),
            "initial_osculating_eccentricity": 0.0,
            "inclination_deg": float(np.rad2deg(self.inclination_rad)),
            "semi_major_axis_m": self.radius_m,
            "two_body_period_s": float(self.period_s),
            "initial_speed_m_s": float(np.sqrt(EARTH_MU / self.radius_m)),
            "target_nodal_rate_deg_day": 360.0 * 86400.0 / TROPICAL_YEAR_S,
            "gravity": "Earth point mass plus J2 (normalized C20 only)",
            "design": "First order secular J2 SSO design. Mean and osculating elements differ.",
            "local_solar_time": "Unspecified. RAAN is a free initial phase, not a selected LTAN.",
        }


def earth_j2():
    earth = gravityEffector.GravBodyData()
    earth.planetName = "earth_planet_data"
    earth.displayName = earth.modelDictionaryKey = "earth"
    earth.mu, earth.radEquator = EARTH_MU, EARTH_RADIUS_M
    earth.isCentralBody = True
    model = sphericalHarmonicsGravityModel.SphericalHarmonicsGravityModel()
    model.muBody, model.radEquator, model.maxDeg = EARTH_MU, EARTH_RADIUS_M, 2
    model.cBar = [[1.0], [0.0, 0.0], [-EARTH_J2 / np.sqrt(5), 0.0, 0.0]]
    model.sBar = [[0.0], [0.0, 0.0], [0.0, 0.0, 0.0]]
    earth.gravityModel = model
    return earth


def acceleration_j2(position):
    r = np.asarray(position, dtype=float)
    radius = np.linalg.norm(r)
    z2 = (r[2] / radius) ** 2
    correction = 1.5 * EARTH_J2 * EARTH_MU * EARTH_RADIUS_M**2 / radius**5
    return -EARTH_MU * r / radius**3 + correction * r * np.array(
        [5 * z2 - 1, 5 * z2 - 1, 5 * z2 - 3]
    )


def body_frame(position, velocity):
    """Body x along track, y along orbit normal, z outward radial."""
    radial = np.asarray(position) / np.linalg.norm(position)
    normal = np.cross(position, velocity)
    normal /= np.linalg.norm(normal)
    along = np.cross(normal, radial)
    return np.column_stack([along, normal, radial])


def frame_from_x(direction, preferred_y):
    x = np.asarray(direction) / np.linalg.norm(direction)
    y = np.asarray(preferred_y) - np.dot(preferred_y, x) * x
    if np.linalg.norm(y) < 1e-8:
        fallback = np.eye(3)[np.argmin(np.abs(x))]
        y = fallback - np.dot(fallback, x) * x
    y /= np.linalg.norm(y)
    return np.column_stack([x, y, np.cross(x, y)])


def earth_rotation(orbit, time):
    jd = orbit.epoch.timestamp() / 86400.0 + 2440587.5
    theta = (
        np.deg2rad((280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360)
        + EARTH_SPIN_RAD_S * time
    )
    c, s = np.cos(theta), np.sin(theta)
    return [[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]]


def sun_position(orbit, time):
    """Low precision geocentric Sun position, used only for Vizard lighting."""
    days = orbit.epoch.timestamp() / 86400.0 + 2440587.5 - 2451545.0 + time / 86400.0
    anomaly = np.deg2rad((357.529 + 0.98560028 * days) % 360)
    longitude = (
        np.deg2rad((280.459 + 0.98564736 * days) % 360)
        + np.deg2rad(1.915) * np.sin(anomaly)
        + np.deg2rad(0.020) * np.sin(2 * anomaly)
    )
    obliquity = np.deg2rad(23.439)
    return 149597870700.0 * np.array(
        [
            np.cos(longitude),
            np.cos(obliquity) * np.sin(longitude),
            np.sin(obliquity) * np.sin(longitude),
        ]
    )


@dataclass
class OrbitTrack:
    time: np.ndarray
    positions: np.ndarray
    velocities: np.ndarray
    orbit: OrbitConfig


def propagate_reference(orbit, periods=1.0, step_s=2.0, mass_kg=6.0):
    """Propagate the COM of the coupled assembly before spring release."""
    orbit.validate()
    sim = SimulationBaseClass.SimBaseClass()
    process = sim.CreateNewProcess("orbit")
    process.addTask(sim.CreateNewTask("orbit_step", macros.sec2nano(step_s)))
    bus = spacecraft.Spacecraft()
    bus.ModelTag = "Coupled_assembly_reference"
    bus.hub.mHub = mass_kg
    bus.hub.IHubPntBc_B = np.diag([0.01, 0.06, 0.06]).tolist()
    bus.hub.r_CN_NInit, bus.hub.v_CN_NInit = orbit.initial_state()
    earth = earth_j2()
    bus.gravField.gravBodies = spacecraft.GravBodyVector([earth])
    sim.AddModelToTask("orbit_step", bus)
    log = bus.scStateOutMsg.recorder()
    sim.AddModelToTask("orbit_step", log)
    duration = np.ceil(orbit.period_s * periods / step_s) * step_s
    sim.InitializeSimulation()
    sim.ConfigureStopTime(macros.sec2nano(duration))
    sim.ExecuteSimulation()
    return OrbitTrack(
        log.times() * macros.NANO2SEC,
        np.asarray(log.r_BN_N),
        np.asarray(log.v_BN_N),
        orbit,
    )
