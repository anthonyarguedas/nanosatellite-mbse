#!/usr/bin/env python3
"""Fast orbit averaged drag screening for a 3 year mission and 5 years afterward.

The pair is represented by its total mass and mean projected area. This mode
propagates mean circular altitude, independently of the detailed deployment.
The fixed medium solar activity assumption is a screening input, not a forecast.
"""

from dataclasses import asdict, dataclass
import argparse
import csv
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from Basilisk import __version__ as basilisk_version
from Basilisk.architecture import messaging
from Basilisk.simulation import msisAtmosphere
from scipy.integrate import solve_ivp

from orbit_environment import EARTH_MU, EARTH_RADIUS_M, EARTH_SPIN_RAD_S, OrbitConfig
from simulate import Config

DAY_S = 86400.0
YEAR_S = 365.25 * DAY_S


def tumbling_pair_area(bus=Config()):
    """Cauchy mean cuboid areas plus the mean side projection of the tether."""
    length, width, height = bus.body_length_m, bus.body_width_m, bus.body_height_m
    buses = length * width + length * height + width * height
    tether = np.pi / 4 * bus.tether_length_m * bus.tether_diameter_m
    return float(buses + tether)


@dataclass(frozen=True)
class Activity:
    name: str
    f107_sfu: float
    ap: float
    color: str


MEDIUM_ACTIVITY = Activity("medium", 140.0, 10.0, "#2171b5")


@dataclass(frozen=True)
class LifetimeConfig:
    mission_years: float = 3.0
    post_mission_years: float = 5.0
    mass_kg: float = 2 * Config().mass_kg
    drag_coefficient: float = 2.2
    mission_area_m2: float = tumbling_pair_area()
    post_mission_area_m2: float = tumbling_pair_area()
    maintain_mission_altitude: bool = False
    reentry_altitude_m: float = 120000.0
    max_step_days: float = 5.0
    record_days: float = 1.0

    @property
    def mission_s(self):
        return self.mission_years * YEAR_S

    @property
    def duration_s(self):
        return (self.mission_years + self.post_mission_years) * YEAR_S

    def validate(self, orbit):
        orbit.validate()
        for name, value in asdict(self).items():
            if name == "maintain_mission_altitude":
                continue
            nonnegative = name in (
                "post_mission_years",
                "drag_coefficient",
                "mission_area_m2",
                "post_mission_area_m2",
            )
            if not np.isfinite(value) or value < 0 or (value == 0 and not nonnegative):
                raise ValueError(f"Invalid lifetime parameter: {name}")
        if not 80000 <= self.reentry_altitude_m < orbit.altitude_m <= 1000000:
            raise ValueError(
                "Require 80 km <= stop altitude < initial altitude <= 1000 km"
            )

    def ballistic_coefficient(self, area):
        return (
            self.mass_kg / (self.drag_coefficient * area)
            if self.drag_coefficient * area
            else None
        )


class MsisSampler:
    """Evaluate Basilisk's native NRLMSISE-00 model with explicit weather inputs."""

    def __init__(self, activity, year=2026):
        self.model = msisAtmosphere.MsisAtmosphere()
        self.model.planetRadius = EARTH_RADIUS_M
        epoch = messaging.EpochMsgPayload()
        epoch.year, epoch.month, epoch.day = year, 1, 1
        self.epoch_msg = messaging.EpochMsg().write(epoch)
        self.model.epochInMsg.subscribeTo(self.epoch_msg)
        planet = messaging.SpicePlanetStateMsgPayload()
        planet.J20002Pfix = np.eye(3).tolist()
        self.planet_msg = messaging.SpicePlanetStateMsg().write(planet)
        self.model.planetPosInMsg.subscribeTo(self.planet_msg)
        self.state_msg = messaging.SCStatesMsg()
        self.model.addSpacecraftToModel(self.state_msg)
        # Indices 0..20 are Ap history, 21 is the 81 day F10.7 average,
        # and 22 is the preceding day's F10.7. Hold each case constant.
        self.weather_msgs = []
        for i in range(23):
            payload = messaging.SwDataMsgPayload()
            payload.dataValue = activity.f107_sfu if i >= 21 else activity.ap
            message = messaging.SwDataMsg().write(payload)
            self.weather_msgs.append(message)
            self.model.swDataInMsgs[i].subscribeTo(message)
        self.model.Reset(0)

    def density(self, position, time_s):
        nanos = int(round(time_s * 1e9))
        payload = messaging.SCStatesMsgPayload()
        payload.r_BN_N = np.asarray(position).tolist()
        self.state_msg.write(payload, nanos)
        self.model.UpdateState(nanos)
        return self.model.envOutMsgs[0].read().neutralDensity


@dataclass
class AtmosphereTable:
    activity: Activity
    altitude_m: np.ndarray
    density_kg_m3: np.ndarray
    drag_work: np.ndarray  # <rho |v_rel| (v dot v_rel)>, SI units

    def work_at(self, altitude_m):
        # Clamping below the stop boundary lets the event solver bracket it.
        return float(
            np.exp(np.interp(altitude_m, self.altitude_m, np.log(self.drag_work)))
        )


def build_atmosphere_table(
    orbit,
    activity,
    stop_altitude_m=120000.0,
    altitude_step_m=10000.0,
    phase_samples=24,
    longitude_samples=4,
    season_samples=4,
):
    """Average over circular phase, node longitude, and seasons.

    LTAN is unspecified, so longitude sampling averages over local solar time.
    Atmospheric co-rotation enters the drag work before averaging. The annual
    mean tables are reused across the mission, with no assumed solar forecast.
    """
    sampler = MsisSampler(activity, orbit.epoch.year)
    samples = []
    inclination = orbit.inclination_rad
    for season in range(season_samples):
        time_s = (season + 0.5) / season_samples * YEAR_S
        for longitude in np.arange(longitude_samples) * 2 * np.pi / longitude_samples:
            x = np.array([np.cos(longitude), np.sin(longitude), 0.0])
            y = np.array(
                [
                    -np.sin(longitude) * np.cos(inclination),
                    np.cos(longitude) * np.cos(inclination),
                    np.sin(inclination),
                ]
            )
            for phase in np.arange(phase_samples) * 2 * np.pi / phase_samples:
                radial = np.cos(phase) * x + np.sin(phase) * y
                along = -np.sin(phase) * x + np.cos(phase) * y
                samples.append((time_s, radial, along))
    altitudes = np.unique(
        np.r_[
            np.arange(stop_altitude_m, orbit.altitude_m, altitude_step_m),
            orbit.altitude_m,
        ]
    )
    densities, work = [], []
    for altitude in altitudes:
        radius = EARTH_RADIUS_M + altitude
        speed = np.sqrt(EARTH_MU / radius)
        local_densities, local_work = [], []
        for time_s, radial, along in samples:
            position, velocity = radius * radial, speed * along
            relative_v = velocity - np.cross([0, 0, EARTH_SPIN_RAD_S], position)
            density = sampler.density(position, time_s)
            local_densities.append(density)
            local_work.append(
                density * np.linalg.norm(relative_v) * np.dot(velocity, relative_v)
            )
        densities.append(np.mean(local_densities))
        work.append(np.mean(local_work))
    return AtmosphereTable(activity, altitudes, np.array(densities), np.array(work))


def altitude_rate(altitude_m, area_m2, config, table):
    radius = EARTH_RADIUS_M + max(altitude_m, config.reentry_altitude_m)
    # E = -mu/(2a), dE/dt = -Cd A/(2m) <rho |v_rel| (v dot v_rel)>.
    return (
        -config.drag_coefficient
        * area_m2
        / config.mass_kg
        * radius**2
        / EARTH_MU
        * table.work_at(altitude_m)
    )


@dataclass
class LifetimeResult:
    activity: Activity
    time_s: np.ndarray
    altitude_m: np.ndarray
    threshold_time_s: float | None

    def altitude_at(self, time_s):
        if time_s > self.time_s[-1] + 1e-6:
            return None
        return float(np.interp(time_s, self.time_s, self.altitude_m))

    def summary(self, config, orbit):
        mission = self.altitude_at(config.mission_s)
        final = self.altitude_at(config.duration_s)
        return {
            "activity": asdict(self.activity),
            "initial_mean_altitude_km": orbit.altitude_m / 1000,
            "mission_end_mean_altitude_km": mission / 1000
            if mission is not None
            else None,
            "post_mission_end_mean_altitude_km": final / 1000
            if final is not None
            else None,
            "mission_decay_km": (orbit.altitude_m - mission) / 1000
            if mission is not None
            else None,
            "post_mission_decay_km": (mission - final) / 1000
            if mission is not None and final is not None
            else None,
            "stop_altitude_reached_year": self.threshold_time_s / YEAR_S
            if self.threshold_time_s is not None
            else None,
            "survives_mission_above_stop_altitude": self.threshold_time_s is None
            or self.threshold_time_s > config.mission_s,
        }


def propagate_lifetime(config, orbit, table):
    config.validate(orbit)
    if (
        table.altitude_m[0] > config.reentry_altitude_m
        or table.altitude_m[-1] < orbit.altitude_m
    ):
        raise ValueError("Atmosphere table must cover the full altitude range")
    if np.any(table.drag_work <= 0) or not np.all(np.isfinite(table.drag_work)):
        raise ValueError("Atmosphere drag work must be finite and positive")
    requested = np.unique(
        np.r_[
            np.arange(0, config.duration_s, config.record_days * DAY_S),
            config.mission_s,
            config.duration_s,
        ]
    )
    times, altitudes = [], []
    altitude, threshold = orbit.altitude_m, None
    phases = (
        (
            0.0,
            config.mission_s,
            config.mission_area_m2,
            config.maintain_mission_altitude,
        ),
        (config.mission_s, config.duration_s, config.post_mission_area_m2, False),
    )
    for lo, hi, area, maintained in phases:
        if hi <= lo:
            continue

        def rate(time, state):
            return [0.0 if maintained else altitude_rate(state[0], area, config, table)]

        def stop(time, state):
            return state[0] - config.reentry_altitude_m

        stop.terminal, stop.direction = True, -1
        solution = solve_ivp(
            rate,
            (lo, hi),
            [altitude],
            method="DOP853",
            events=stop,
            dense_output=True,
            rtol=1e-9,
            atol=0.001,
            max_step=config.max_step_days * DAY_S,
        )
        if not solution.success:
            raise RuntimeError(solution.message)
        end = solution.t[-1]
        samples = requested[(requested >= lo) & (requested <= end)]
        if len(solution.t_events[0]):
            threshold = float(solution.t_events[0][0])
            samples = np.unique(np.r_[samples, threshold])
        for time, value in zip(samples, solution.sol(samples)[0]):
            if times and abs(time - times[-1]) < 1e-6:
                continue
            times.append(float(time))
            altitudes.append(float(value))
        altitude = float(solution.y[0, -1])
        if threshold is not None:
            altitudes[-1] = config.reentry_altitude_m
            break
    return LifetimeResult(
        table.activity, np.array(times), np.array(altitudes), threshold
    )


def export_lifetime(results, tables, config, orbit, output, vizard_case=None):
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        "model": "Orbit averaged circular drag with native Basilisk NRLMSISE-00",
        "basilisk_version": basilisk_version,
        "config": asdict(config),
        "orbit": {
            **asdict(orbit),
            "interpretation": "Initial mean circular orbit, not osculating J2 altitude",
            "inclination_deg": float(np.rad2deg(orbit.inclination_rad)),
            "reference_radius_m": EARTH_RADIUS_M,
            "j2_role": "Initial SSO inclination design only. No secular plane or periodic J2 propagation.",
        },
        "year_days": YEAR_S / DAY_S,
        "mission_end_year": config.mission_years,
        "post_mission_end_year": config.mission_years + config.post_mission_years,
        "mission_ballistic_coefficient_kg_m2": config.ballistic_coefficient(
            config.mission_area_m2
        ),
        "post_mission_ballistic_coefficient_kg_m2": config.ballistic_coefficient(
            config.post_mission_area_m2
        ),
        "assumptions": [
            "The two buses and tether remain one intact pair. Mass is constant.",
            "Default areas are isotropic mean projected areas with no mutual shadowing. Cd is assumed, not measured.",
            "Medium activity is held constant at F10.7 = 140 sfu and Ap = 10. This is a screening assumption, not a weather forecast.",
            "Density and drag work are averaged over orbital phase, node longitude and seasons. LTAN is unspecified.",
            "Atmosphere co-rotation is included. Atmospheric winds are omitted.",
            "Altitude is a mean circular altitude above the equatorial reference radius. J2 periodic altitude oscillations are omitted.",
            "There is no stationkeeping unless maintain_mission_altitude is enabled. That option assumes ideal orbit maintenance without a fuel calculation.",
            "Propagation stops at the chosen altitude boundary. No atmospheric entry or burnup is modeled.",
            "Tether oscillations, collisions, attitude evolution, solar radiation pressure and third body effects are omitted.",
            "This is a separate lifetime screening model. It does not continue the millisecond deployment dynamics.",
        ],
        "cases": [result.summary(config, orbit) for result in results],
        "visualization": "The reduced lifetime model produces numerical results only. simulate.py generates mission.bin from the live coupled orbital, tether and contact dynamics.",
    }
    (output / "lifetime_results.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    with (output / "lifetime.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["activity", "time_s", "elapsed_years", "mean_altitude_km", "phase"]
        )
        for result in results:
            for time, altitude in zip(result.time_s, result.altitude_m):
                phase = "mission" if time <= config.mission_s else "post_mission"
                writer.writerow(
                    [
                        result.activity.name,
                        f"{time:.6f}",
                        f"{time / YEAR_S:.9f}",
                        f"{altitude / 1000:.9f}",
                        phase,
                    ]
                )
    with (output / "lifetime_atmosphere.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["activity", "altitude_m", "mean_density_kg_m3", "mean_drag_work_SI"]
        )
        for table in tables:
            for altitude, density, work in zip(
                table.altitude_m, table.density_kg_m3, table.drag_work
            ):
                writer.writerow([table.activity.name, altitude, density, work])
    return summary


def plot_lifetime(results, config, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    for result in results:
        case = result.activity
        axis.plot(
            result.time_s / YEAR_S,
            result.altitude_m / 1000,
            color=case.color,
            label=f"{case.name.capitalize()}: F10.7 = {case.f107_sfu:g}, Ap = {case.ap:g}",
        )
        if result.threshold_time_s is not None:
            axis.plot(
                result.threshold_time_s / YEAR_S,
                config.reentry_altitude_m / 1000,
                "o",
                color=case.color,
            )
    end_year = config.mission_years + config.post_mission_years
    axis.axvspan(config.mission_years, end_year, color="0.5", alpha=0.08)
    axis.axvline(config.mission_years, color="0.4", linestyle="--", label="Mission end")
    if any(result.threshold_time_s is not None for result in results):
        axis.axhline(
            config.reentry_altitude_m / 1000,
            color="0.6",
            linestyle=":",
            label="Propagation stop boundary",
        )
    axis.set(
        xlabel="Years since launch",
        ylabel="Mean circular altitude (km)",
        xlim=(0, end_year),
        title="Orbital decay screening: medium solar activity",
    )
    axis.grid(alpha=0.25)
    axis.legend()
    fig.savefig(output / "lifetime.png", dpi=180)
    fig.savefig(output / "lifetime.svg")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mission-years", type=float, default=3.0)
    parser.add_argument("--post-mission-years", type=float, default=5.0)
    parser.add_argument("--altitude-km", type=float, default=600.0)
    parser.add_argument("--epoch", default="2026-01-01T00:00:00Z")
    parser.add_argument(
        "--mass-kg", type=float, default=6.0, help="Total mass of the pair"
    )
    parser.add_argument("--cd", type=float, default=2.2)
    parser.add_argument(
        "--mission-area-m2",
        type=float,
        default=tumbling_pair_area(),
        help="Mean area of the whole pair",
    )
    parser.add_argument(
        "--post-mission-area-m2",
        type=float,
        default=tumbling_pair_area(),
        help="Mean area of the whole pair",
    )
    parser.add_argument(
        "--maintain-mission-altitude",
        action="store_true",
        help="Assume ideal stationkeeping during the mission only",
    )
    parser.add_argument("--max-step-days", type=float, default=5.0)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "output")
    parser.add_argument("--no-vizard", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the completed continuous mission.bin, generated separately by simulate.py",
    )
    parser.add_argument("--vizard-app", type=Path)
    args = parser.parse_args()
    orbit = OrbitConfig(altitude_m=args.altitude_km * 1000, epoch_utc=args.epoch)
    config = LifetimeConfig(
        mission_years=args.mission_years,
        post_mission_years=args.post_mission_years,
        mass_kg=args.mass_kg,
        drag_coefficient=args.cd,
        mission_area_m2=args.mission_area_m2,
        post_mission_area_m2=args.post_mission_area_m2,
        maintain_mission_altitude=args.maintain_mission_altitude,
        max_step_days=args.max_step_days,
    )
    try:
        config.validate(orbit)
        if args.open and args.no_vizard:
            raise ValueError("--open requires Vizard export")
    except ValueError as error:
        parser.error(str(error))
    started = perf_counter()
    print("Averaging native NRLMSISE-00 atmosphere: medium activity...", flush=True)
    table = build_atmosphere_table(orbit, MEDIUM_ACTIVITY, config.reentry_altitude_m)
    tables = [table]
    results = [propagate_lifetime(config, orbit, table)]
    summary = export_lifetime(
        results,
        tables,
        config,
        orbit,
        args.output,
        vizard_case=None,
    )
    plot_lifetime(results, config, args.output)
    if args.open:
        from vizard_scene import open_vizard

        path = args.output / "mission.bin"
        status_path = args.output / "run_status.json"
        if (
            status_path.exists()
            and json.loads(status_path.read_text())["status"] != "completed"
        ):
            parser.error(
                "The continuous mission is still running or was interrupted. See run_status.json."
            )
        if not path.exists():
            parser.error(
                "Generate the continuous Vizard trajectory with simulate.py first."
            )
        open_vizard(path, args.vizard_app)
    print(json.dumps(summary["cases"], indent=2))
    print(
        f"Elapsed: {perf_counter() - started:.2f} s. Outputs: {args.output.resolve()}"
    )
    print(
        "Screening estimate only. Fixed medium solar activity is not a weather forecast."
    )


if __name__ == "__main__":
    main()
