#!/usr/bin/env python3
"""Basilisk simulation of two 1.5U CubeSats with a slack, elastic tether.

Uses synchronized spacecraft from scenarioFormationBasic and tension only
coupling adapted from scenarioConstrainedDynamics. The command line runs a
600 km Sun synchronous orbit with Earth J2 gravity and medium activity drag.
The default continuous run covers three days and streams its states to disk.
The library retains a free space case for analytical regression tests.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

import numpy as np
from Basilisk import __version__ as basilisk_version
from Basilisk.architecture import sysModel
from Basilisk.simulation import extForceTorque, spacecraft, svIntegrators
from Basilisk.utilities import SimulationBaseClass, macros

from orbit_environment import OrbitConfig


@dataclass(frozen=True)
class Config:
    mass_kg: float = 3.0  # CDS Rev. 14.1, Table 1: typical 1.5U maximum
    body_length_m: float = 0.1702  # rail envelope along separation axis
    body_width_m: float = 0.10
    body_height_m: float = 0.10
    tether_length_m: float = 3.0  # between facing attachment points
    tether_diameter_m: float = 0.0005  # assumed nylon monofilament
    nylon_modulus_pa: float = 2.0e9  # assumed effective axial modulus
    spring_stroke_m: float = 0.02
    max_relative_speed_m_s: float = 0.10
    duration_s: float = 50.0
    step_s: float = 0.001
    record_s: float = 0.005
    late_record_s: float = 0.1
    dense_duration_s: float = 120.0
    restitution: float = 0.3  # illustrative frictionless collision response

    @property
    def reduced_mass_kg(self) -> float:
        return self.mass_kg / 2.0

    @property
    def spring_energy_j(self) -> float:
        return 0.5 * self.reduced_mass_kg * self.max_relative_speed_m_s**2

    @property
    def spring_stiffness_n_m(self) -> float:
        return 2.0 * self.spring_energy_j / self.spring_stroke_m**2

    @property
    def tether_stiffness_n_m(self) -> float:
        area = np.pi * self.tether_diameter_m**2 / 4.0
        return self.nylon_modulus_pa * area / self.tether_length_m

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if name == "restitution":
                if not np.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError("restitution must be between zero and one")
            elif not np.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if self.late_record_s < self.record_s:
            raise ValueError("late_record_s must be at least record_s")
        if self.spring_stroke_m >= self.tether_length_m:
            raise ValueError("The spring stroke must be shorter than the tether")
        for name in ("step_s", "record_s", "late_record_s", "duration_s"):
            nanos = getattr(self, name) * 1e9
            if abs(nanos - round(nanos)) > 1e-3:
                raise ValueError(f"{name} must be an integer number of nanoseconds")
        for name in ("record_s", "late_record_s", "duration_s"):
            ratio = getattr(self, name) / self.step_s
            if abs(ratio - round(ratio)) > 1e-6:
                raise ValueError(f"{name} must be a multiple of step_s")
        if (
            self.step_s
            * np.sqrt(
                max(self.spring_stiffness_n_m, self.tether_stiffness_n_m)
                / self.reduced_mass_kg
            )
            > 0.05
        ):
            raise ValueError("Use a smaller step to resolve the spring and tether")


def midpoint_force(
    gap: float,
    speed: float,
    config: Config,
    spring_available: bool,
    reduced_mass: float | None = None,
) -> float:
    """Force on the right bus over the next fixed integration interval.

    Solve the scalar implicit midpoint equations by enumerating their three
    linear regimes. Equal and opposite forces preserve center of mass motion.
    """
    mu, dt = reduced_mass or config.reduced_mass_kg, config.step_s
    regimes = []
    if spring_available:
        regimes.append((config.spring_stiffness_n_m, config.spring_stroke_m, "spring"))
    regimes.extend(
        [
            (0.0, 0.0, "slack"),
            (config.tether_stiffness_n_m, config.tether_length_m, "taut"),
        ]
    )
    for stiffness, equilibrium, regime in regimes:
        a = stiffness * (equilibrium - gap - 0.5 * speed * dt)
        denominator = 1.0 + 0.25 * stiffness * dt**2 / mu
        force = a / denominator
        middle_gap = gap + 0.5 * speed * dt + 0.25 * force * dt**2 / mu
        in_spring = spring_available and middle_gap < config.spring_stroke_m
        in_tether = middle_gap > config.tether_length_m
        if (
            (regime == "spring" and in_spring)
            or (regime == "slack" and not in_spring and not in_tether)
            or (regime == "taut" and in_tether)
        ):
            return float(force)
    raise RuntimeError("No consistent force regime")


class Coupling(sysModel.SysModel):
    """Read both updated hub states, then set forces for their NEXT interval."""

    def __init__(self, buses, effectors, config: Config):
        super().__init__()
        self.ModelTag = "spring_and_tension_only_tether"
        self.buses = buses
        self.effectors = effectors
        self.config = config
        self.spring_available = True
        from contact import CollisionResolver

        self.contact = CollisionResolver(buses, config)
        self.last_dynamic_time = -1e30

    def UpdateState(self, current_nanos):
        payloads = [bus.scStateOutMsg.read() for bus in self.buses]
        time = current_nanos * 1e-9
        if not self.spring_available and self.contact.resolve(payloads, time):
            payloads = [bus.scStateOutMsg.read() for bus in self.buses]
        left, right = payloads
        gap = right.r_BN_N[0] - left.r_BN_N[0] - self.config.body_length_m
        speed = right.v_BN_N[0] - left.v_BN_N[0]
        if gap >= self.config.spring_stroke_m:
            self.spring_available = False
        force = midpoint_force(gap, speed, self.config, self.spring_available)
        if force < -1e-3:
            self.last_dynamic_time = time
        self.effectors[0].extForce_N = [-force, 0.0, 0.0]
        self.effectors[1].extForce_N = [force, 0.0, 0.0]


class RecordingCadence(sysModel.SysModel):
    """Dense recording around release, tether snatch and actual impacts."""

    def __init__(self, logs, coupling, config):
        super().__init__()
        self.ModelTag = "adaptive_state_recording"
        self.logs, self.coupling, self.config = logs, coupling, config
        self.interval = None

    def UpdateState(self, current_nanos):
        time = current_nanos * 1e-9
        impact = self.coupling.contact.last_impact_time
        dynamic = max(impact, self.coupling.last_dynamic_time)
        dense = time <= self.config.dense_duration_s or time - dynamic < 2.0
        interval = macros.sec2nano(
            self.config.record_s if dense else self.config.late_record_s
        )
        if impact == time:
            interval = 0
        if interval != self.interval:
            for log in self.logs:
                log.updateTimeInterval(interval)
            self.interval = interval


@dataclass
class Result:
    name: str
    time: np.ndarray
    positions: np.ndarray  # [sample, bus, inertial axis], meters
    velocities: np.ndarray  # [sample, bus, inertial axis], meters/second
    gap: np.ndarray
    speed: np.ndarray
    tension: np.ndarray
    energy: np.ndarray
    orbit: OrbitConfig | None = None
    attitudes: np.ndarray | None = None
    angular_velocities: np.ndarray | None = None
    anchor_positions: np.ndarray | None = None
    anchor_velocities: np.ndarray | None = None
    collision_events: list[dict] = field(default_factory=list)
    contact_statistics: dict = field(default_factory=dict)
    drag_statistics: dict = field(default_factory=dict)

    def summary(self, config: Config) -> dict:
        taut = np.flatnonzero(self.gap >= config.tether_length_m)
        moving = np.flatnonzero(self.speed > 1e-8)
        stopped = np.flatnonzero((self.time > 1.0) & (np.abs(self.speed) < 1e-8))
        first_taut = None
        if len(taut):
            i = int(taut[0])
            first_taut = float(self.time[i])
            if i:
                first_taut = float(
                    np.interp(
                        config.tether_length_m,
                        self.gap[i - 1 : i + 1],
                        self.time[i - 1 : i + 1],
                    )
                )
        first_stop = (
            float(self.time[stopped[0]]) if len(stopped) and len(moving) else None
        )
        momentum = config.mass_kg * self.velocities.sum(axis=1)
        return {
            "name": self.name,
            "first_taut_s": first_taut,
            "duration_s": float(self.time[-1]),
            "collision_episodes": len(self.collision_events),
            "contact_statistics": self.contact_statistics,
            "first_sample_at_rest_s": first_stop,
            "maximum_attachment_separation_m": float(self.gap.max()),
            "maximum_center_separation_m": float(
                np.linalg.norm(
                    self.positions[:, 1] - self.positions[:, 0], axis=1
                ).max()
            ),
            "time_of_maximum_separation_s": float(self.time[self.gap.argmax()]),
            "maximum_relative_speed_m_s": float(
                np.linalg.norm(
                    self.velocities[:, 1] - self.velocities[:, 0], axis=1
                ).max()
            ),
            "maximum_attachment_separation_rate_m_s": float(np.abs(self.speed).max()),
            "initial_spring_release_center_speed_m_s": float(
                np.linalg.norm(
                    self.velocities[self.time <= 1, 1]
                    - self.velocities[self.time <= 1, 0],
                    axis=1,
                ).max()
            ),
            "peak_tension_n": float(self.tension.max()),
            "maximum_tether_strain": float(
                max(0, self.gap.max() / config.tether_length_m - 1)
            ),
            "maximum_total_momentum_kg_m_s": float(
                np.linalg.norm(momentum, axis=1).max()
            )
            if self.orbit is None
            else None,
            "final_mechanical_energy_j": float(self.energy[-1]),
            "maximum_energy_error_fraction": float(
                np.abs(self.energy / config.spring_energy_j - 1).max()
            )
            if self.orbit is None and not self.collision_events
            else None,
        }


def build_simulation(config: Config, orbit: OrbitConfig | None = None, drag=None):
    """Build the same live spacecraft for memory or streaming recording."""
    config.validate()
    if drag is not None and orbit is None:
        raise ValueError("Atmospheric drag requires an Earth orbit")
    sim = SimulationBaseClass.SimBaseClass()
    task = "dynamics"
    process = sim.CreateNewProcess("deployment")
    process.addTask(sim.CreateNewTask(task, macros.sec2nano(config.step_s)))
    buses = [spacecraft.Spacecraft(), spacecraft.Spacecraft()]
    effectors = [extForceTorque.ExtForceTorque(), extForceTorque.ExtForceTorque()]
    length, width, height = (
        config.body_length_m,
        config.body_width_m,
        config.body_height_m,
    )
    inertia = (
        config.mass_kg
        / 12.0
        * np.diag([width**2 + height**2, length**2 + height**2, length**2 + width**2])
    )
    for i, (bus, effector) in enumerate(zip(buses, effectors)):
        bus.ModelTag = f"CubeSat_{'A' if i == 0 else 'B'}"
        bus.hub.mHub = config.mass_kg
        bus.hub.IHubPntBc_B = inertia.tolist()
        bus.hub.r_CN_NInit = [(i - 0.5) * length, 0.0, 0.0]
        bus.hub.v_CN_NInit = [0.0, 0.0, 0.0]
        bus.hub.sigma_BNInit = [0.0, 0.0, 0.0]
        bus.hub.omega_BN_BInit = [0.0, 0.0, 0.0]
        # No messages are used by these effectors. extForce_N is held constant
        # over each interval and consumed directly by their native C++ force call.
        bus.addDynamicEffector(effector)
        sim.AddModelToTask(task, bus, 20)
    if orbit is not None:
        from orbital_deployment import initialize_orbit

        sim._earth = initialize_orbit(buses, config, orbit)
    integrator = svIntegrators.svIntegratorRK4(buses[0])
    buses[0].setIntegrator(integrator)
    buses[0].syncDynamicsIntegration(buses[1])
    sim._integrator = integrator
    if orbit is None:
        coupling = Coupling(buses, effectors, config)
    else:
        from orbital_deployment import OrbitCoupling

        coupling = OrbitCoupling(buses, effectors, config, drag=drag)
    sim.AddModelToTask(task, coupling, 10)
    return sim, buses, coupling, inertia


def simulate(
    config: Config,
    vizard_path: Path | None = None,
    orbit: OrbitConfig | None = None,
    drag=None,
) -> Result:
    sim, buses, coupling, inertia = build_simulation(config, orbit, drag)
    task, length = "dynamics", config.body_length_m
    logs = [
        bus.scStateOutMsg.recorder(macros.sec2nano(config.record_s)) for bus in buses
    ]
    for log in logs:
        sim.AddModelToTask(task, log, 0)
    cadence = RecordingCadence(logs, coupling, config)
    sim.AddModelToTask(task, cadence, 5)
    sim.InitializeSimulation()
    sim.ConfigureStopTime(macros.sec2nano(config.duration_s))
    sim.ExecuteSimulation()
    end_nanos = macros.sec2nano(config.duration_s)
    for log in logs:
        if log.times()[-1] != end_nanos:
            log.updateTimeInterval(0)
            log.UpdateState(end_nanos)
    time = logs[0].times() * macros.NANO2SEC
    positions = np.stack([log.r_BN_N for log in logs], axis=1)
    velocities = np.stack([log.v_BN_N for log in logs], axis=1)
    gap = positions[:, 1, 0] - positions[:, 0, 0] - length
    speed = velocities[:, 1, 0] - velocities[:, 0, 0]
    attitudes = angular_velocities = anchors = anchor_velocities = None
    if orbit is not None:
        from orbital_deployment import record_geometry

        attitudes = np.stack([log.sigma_BN for log in logs], axis=1)
        angular_velocities = np.stack([log.omega_BN_B for log in logs], axis=1)
        anchors, anchor_velocities, gap, speed = record_geometry(
            positions, velocities, attitudes, angular_velocities, config
        )
    extension = np.maximum(gap - config.tether_length_m, 0.0)
    tension = config.tether_stiffness_n_m * extension
    # The release spring is a one-shot force and never fires on a collision.
    spring_released = np.maximum.accumulate(gap) >= config.spring_stroke_m
    compression = np.where(
        spring_released, 0.0, np.maximum(config.spring_stroke_m - gap, 0.0)
    )
    relative_velocities = velocities - velocities.mean(axis=1, keepdims=True)
    energy = (
        0.5 * config.mass_kg * (relative_velocities**2).sum(axis=(1, 2))
        + 0.5 * config.spring_stiffness_n_m * compression**2
        + 0.5 * config.tether_stiffness_n_m * extension**2
    )
    if angular_velocities is not None:
        energy += 0.5 * np.einsum(
            "nbi,ij,nbj->n", angular_velocities, inertia, angular_velocities
        )
    result = Result(
        "Tether deployment",
        time,
        positions,
        velocities,
        gap,
        speed,
        tension,
        energy,
        orbit,
        attitudes,
        angular_velocities,
        anchors,
        anchor_velocities,
        [dict(event) for event in coupling.contact.events],
        {
            "impulse_count": coupling.contact.total_impulses,
            "maximum_penetration_m": coupling.contact.maximum_penetration_m,
            "kinetic_energy_lost_j": coupling.contact.total_energy_lost_j,
        },
        drag.summary() if drag is not None else {},
    )
    if vizard_path is not None:
        from vizard_scene import export_vizard

        export_vizard([result], config, vizard_path)
    return result


def export_results(results: list[Result], config: Config, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    values = asdict(config)
    orbit = results[0].orbit
    summary = {
        "basilisk_version": basilisk_version,
        "environment": "Earth centered inertial frame, point mass plus J2"
        if orbit
        else "Free space",
        "config": values,
        "drag": results[0].drag_statistics or None,
        "orbit": orbit.summary() if orbit else None,
        "spring_energy_j": config.spring_energy_j,
        "spring_stiffness_n_m": config.spring_stiffness_n_m,
        "tether_stiffness_n_m": config.tether_stiffness_n_m,
        "free_space_analytical_catch_s": float(
            np.pi / 2 * np.sqrt(config.reduced_mass_kg / config.spring_stiffness_n_m)
            + (config.tether_length_m - config.spring_stroke_m)
            / config.max_relative_speed_m_s
        ),
        "scenarios": [r.summary(config) for r in results],
        "notes": [
            "One continuous integration of the same two spacecraft. Spring release is at t=0.",
            "Frictionless cuboid impacts use normal restitution and small penetration correction. No avoidance, relatching, damage or spring refiring.",
            "Orbital gravity and attachment torques can change subsequent relative motion.",
            "Relative mechanical energy excludes the common orbital energy and is not conserved under tidal forcing.",
        ],
    }
    result = results[0]
    headers = [
        "time_s",
        "attachment_distance_m",
        "center_distance_m",
        "attachment_separation_rate_m_s",
        "tension_n",
        "relative_mechanical_energy_j",
    ]
    columns = [
        result.time,
        result.gap,
        np.linalg.norm(result.positions[:, 1] - result.positions[:, 0], axis=1),
        result.speed,
        result.tension,
        result.energy,
    ]
    for label, array in (
        ("position", result.positions),
        ("velocity", result.velocities),
        ("mrp", result.attitudes),
        ("omega_body", result.angular_velocities),
        ("anchor", result.anchor_positions),
    ):
        if array is None:
            continue
        columns.append(array.reshape(len(result.time), -1))
        headers.extend(
            f"{label}_{bus}_{axis}" for bus in ("A", "B") for axis in ("x", "y", "z")
        )
    np.savetxt(
        output / "mission.csv",
        np.column_stack(columns),
        delimiter=",",
        comments="",
        fmt="%.16g",
        header=",".join(headers),
    )
    summary["collision_events"] = result.collision_events
    summary["release_time_s"] = 0.0
    if orbit is not None:
        from orbit_environment import EARTH_RADIUS_M

        altitude = (
            np.linalg.norm(result.positions.mean(axis=1), axis=1) - EARTH_RADIUS_M
        )
        summary["continuous_run"] = {
            "duration_s": float(result.time[-1]),
            "design_orbits": float(result.time[-1] / orbit.period_s),
            "minimum_com_altitude_m": float(altitude.min()),
            "maximum_com_altitude_m": float(altitude.max()),
            "single_trajectory_for_all_views": True,
        }
    (output / "results.json").write_text(json.dumps(summary, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "output")
    parser.add_argument(
        "--mass", type=float, default=3.0, help="Mass of each CubeSat in kg"
    )
    duration_args = parser.add_mutually_exclusive_group()
    duration_args.add_argument(
        "--duration", type=float, help="Continuous run in seconds"
    )
    duration_args.add_argument(
        "--days", type=float, help="Continuous run in days (default: 3)"
    )
    duration_args.add_argument(
        "--orbits", type=float, help="Number of design orbital periods"
    )
    parser.add_argument("--step", type=float, default=0.005)
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream live states to disk (automatic for runs over one hour)",
    )
    parser.add_argument(
        "--no-drag",
        action="store_true",
        help="Disable atmospheric drag for regression checks",
    )
    parser.add_argument(
        "--cd", type=float, default=2.2, help="Assumed drag coefficient"
    )
    parser.add_argument("--max-output-gib", type=float, default=28.0)
    parser.add_argument("--reserve-free-gib", type=float, default=5.0)
    parser.add_argument(
        "--restitution",
        type=float,
        default=0.3,
        help="Normal collision restitution, between zero and one",
    )
    parser.add_argument("--dense-duration", type=float, default=120.0)
    parser.add_argument("--altitude-km", type=float, default=600.0)
    parser.add_argument("--raan-deg", type=float, default=0.0)
    parser.add_argument("--epoch", default="2026-01-01T00:00:00Z")
    parser.add_argument(
        "--free-space",
        action="store_true",
        help="Use the analytical gravity free regression case",
    )
    parser.add_argument("--skip-overview", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--vizard", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--vizard-only", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--vizard-app", type=Path)
    parser.add_argument(
        "--open", action="store_true", help="Open the generated scene in Vizard"
    )
    args = parser.parse_args()
    if (
        not np.isfinite(args.step)
        or args.step <= 0
        or (
            args.orbits is not None
            and (not np.isfinite(args.orbits) or args.orbits <= 0)
        )
    ):
        parser.error("step and orbits must be finite and positive")
    if not np.isfinite(args.cd) or args.cd < 0:
        parser.error("cd must be finite and nonnegative")
    orbit = (
        None
        if args.free_space
        else OrbitConfig(args.altitude_km * 1000, args.raan_deg, args.epoch)
    )
    if args.duration is not None:
        requested_duration = args.duration
    elif args.days is not None:
        requested_duration = args.days * 86400.0
    elif args.orbits is not None:
        if orbit is None:
            parser.error("--orbits requires an Earth orbit")
        requested_duration = orbit.period_s * args.orbits
    else:
        requested_duration = 3 * 86400.0 if orbit else 50.0
    if not np.isfinite(requested_duration) or requested_duration <= 0:
        parser.error("duration must be finite and positive")
    duration = float(np.ceil(requested_duration / args.step) * args.step)
    config = Config(
        mass_kg=args.mass,
        duration_s=duration,
        step_s=args.step,
        record_s=float(np.ceil(0.01 / args.step) * args.step),
        late_record_s=float(np.ceil(0.1 / args.step) * args.step),
        dense_duration_s=args.dense_duration,
        restitution=args.restitution,
    )
    config.validate()
    output = args.output.resolve()
    streaming = args.stream or config.duration_s > 3600
    if streaming and orbit is None:
        parser.error("Streaming runs require an Earth orbit")
    drag = None
    if orbit is not None and not args.no_drag:
        from atmospheric_drag import MediumDrag

        drag = MediumDrag.from_orbit(config, orbit, args.cd)
    print(
        f"Simulating release and {config.duration_s / 3600:.2f} hours of continuous motion with Basilisk {basilisk_version}...",
        flush=True,
    )
    if streaming:
        from mission_stream import StreamSettings, run_streaming

        settings = StreamSettings(
            max_output_gib=args.max_output_gib, reserve_free_gib=args.reserve_free_gib
        )
        import signal

        def stop_requested(signum, frame):
            raise KeyboardInterrupt(f"Stopped by signal {signum}")

        previous_handler = signal.signal(signal.SIGTERM, stop_requested)
        try:
            summary = run_streaming(
                config,
                orbit,
                output,
                drag=drag,
                settings=settings,
                open_result=args.open,
                app=args.vizard_app,
            )
        finally:
            signal.signal(signal.SIGTERM, previous_handler)
        print(json.dumps(summary["scenarios"], indent=2))
        return
    result = simulate(config, orbit=orbit, drag=drag)
    from vizard_scene import export_vizard, open_vizard

    export_results([result], config, output)
    target = export_vizard([result], config, output / "mission.bin")
    if orbit:
        print(json.dumps(orbit.summary(), indent=2))
    print(json.dumps(result.summary(config), indent=2))
    print(f"Continuous orbit and deployment: {target}")
    if args.open:
        open_vizard(target, args.vizard_app)


if __name__ == "__main__":
    main()
