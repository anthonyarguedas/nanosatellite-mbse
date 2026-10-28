"""Bounded-memory recording of one continuous Basilisk orbital deployment.

Both spacecraft remain integrated at the configured dynamics step. Only output
sampling changes. Vizard packets and CSV rows use those same live hub states.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import json
import os
from pathlib import Path
import shutil
import time

import numpy as np
from Basilisk import __version__ as basilisk_version
from Basilisk.architecture import sysModel
from Basilisk.utilities import macros

from orbit_environment import EARTH_MU, EARTH_RADIUS_M
from simulate import build_simulation
from vizard_scene import (
    LiveScene,
    configure_deployment_models,
    deployment_objects,
    open_vizard,
    setup_viz,
)


@dataclass(frozen=True)
class StreamSettings:
    initial_s: float = 0.02
    active_s: float = 0.05
    quiet_s: float = 0.2
    progress_s: float = 600.0
    max_output_gib: float = 28.0
    reserve_free_gib: float = 5.0

    def validate(self, config):
        for name, value in asdict(self).items():
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        for interval in (self.initial_s, self.active_s, self.quiet_s):
            if interval < config.step_s:
                raise ValueError(
                    "Recording intervals must be at least the dynamics step"
                )


class MissionRecorder(sysModel.SysModel):
    def __init__(self, sim, coupling, config, orbit, output, settings):
        super().__init__()
        self.ModelTag = "live_orbit_tether_recording"
        self.coupling, self.config, self.orbit = coupling, config, orbit
        self.output, self.settings = Path(output), settings
        self.output.mkdir(parents=True, exist_ok=True)
        self.scene = LiveScene(config, orbit)
        self.viz = setup_viz(
            sim,
            "dynamics",
            self.scene,
            deployment_objects(self.scene),
            self.output / "mission.bin.part",
            overview=True,
            register=False,
        )
        configure_deployment_models(self.viz, config)
        self.viz.settings.viewCameraViewHUD = -1
        self.csv_file = (self.output / "mission.csv.part").open(
            "w", newline="", buffering=1024 * 1024
        )
        self.events_file = (self.output / "collision_events.jsonl.part").open("w")
        self.csv = csv.writer(self.csv_file)
        header = [
            "time_s",
            "attachment_distance_m",
            "center_distance_m",
            "attachment_separation_rate_m_s",
            "tension_n",
            "relative_mechanical_energy_j",
        ]
        for label in ("position", "velocity", "mrp", "omega_body", "anchor"):
            header.extend(
                f"{label}_{bus}_{axis}"
                for bus in ("A", "B")
                for axis in ("x", "y", "z")
            )
        header.extend(["drag_work_j", "drag_power_w"])
        self.csv.writerow(header)
        self.started = time.perf_counter()
        self.current_time = 0.0
        self.last_record_nanos = -(10**18)
        self.next_progress = 0.0
        self.next_storage_check = 0.0
        self.end_nanos = macros.sec2nano(config.duration_s)
        self.samples, self.logged_events, self.last_seen_episode = 0, 0, 0
        self.first_event, self.last_event = None, None
        self.initial_states, self.last_states = None, None
        self.first_taut = None
        self.min_altitude, self.max_altitude = None, None
        self.max_gap, self.max_centers, self.max_tension, self.final_energy = (
            0.0,
            0.0,
            0.0,
            0.0,
        )
        length, width, height = (
            config.body_length_m,
            config.body_width_m,
            config.body_height_m,
        )
        self.inertia = (
            config.mass_kg
            / 12
            * np.diag(
                [width**2 + height**2, length**2 + height**2, length**2 + width**2]
            )
        )

    def Reset(self, current_nanos):
        # VizInterface is stepped only when an output sample is due.
        self.viz.Reset(current_nanos)

    def _drain_events(self, final=False):
        events = self.coupling.contact.events
        while events and (
            final
            or len(events) > 1
            or self.current_time - events[0]["end_time_s"] >= 0.2
        ):
            event = events.pop(0)
            self.events_file.write(json.dumps(event, allow_nan=False) + "\n")
            self.logged_events += 1
            if self.first_event is None:
                self.first_event = dict(event)
            self.last_event = dict(event)

    def _sample(self, nanos):
        states = self.coupling.states
        if states is None or not np.all(np.isfinite(states)):
            raise RuntimeError("Nonfinite or missing live spacecraft state")
        anchors, gap, speed = self.scene.write(states, nanos)
        self.viz.UpdateState(nanos)
        positions, velocities = states[:, :3], states[:, 3:6]
        center_distance = np.linalg.norm(positions[1] - positions[0])
        extension = max(0.0, gap - self.config.tether_length_m)
        compression = (
            max(0.0, self.config.spring_stroke_m - gap)
            if self.coupling.spring_available
            else 0.0
        )
        tension = self.config.tether_stiffness_n_m * extension
        relative_v = velocities - velocities.mean(axis=0)
        energy = (
            0.5 * self.config.mass_kg * np.sum(relative_v**2)
            + 0.5 * self.config.spring_stiffness_n_m * compression**2
            + 0.5 * self.config.tether_stiffness_n_m * extension**2
            + 0.5
            * np.einsum("bi,ij,bj->", states[:, 9:12], self.inertia, states[:, 9:12])
        )
        drag = self.coupling.drag
        row = [self.current_time, gap, center_distance, speed, tension, energy]
        for values in (positions, velocities, states[:, 6:9], states[:, 9:12], anchors):
            row.extend(values.reshape(-1))
        row.extend([drag.work_j if drag else 0.0, drag.power_w if drag else 0.0])
        self.csv.writerow([f"{float(value):.16g}" for value in row])
        self.last_states = states.copy()
        if self.initial_states is None:
            self.initial_states = states.copy()
        if self.first_taut is None and gap >= self.config.tether_length_m:
            self.first_taut = self.current_time
        altitude = float(np.linalg.norm(positions.mean(axis=0)) - EARTH_RADIUS_M)
        self.min_altitude = (
            altitude if self.min_altitude is None else min(self.min_altitude, altitude)
        )
        self.max_altitude = (
            altitude if self.max_altitude is None else max(self.max_altitude, altitude)
        )
        self.max_gap, self.max_centers = (
            max(self.max_gap, gap),
            max(self.max_centers, center_distance),
        )
        self.max_tension, self.final_energy = (
            max(self.max_tension, tension),
            float(energy),
        )
        self.samples += 1
        self.last_record_nanos = nanos
        self.last_seen_episode = self.coupling.contact.total_episodes
        self._drain_events()

    def _output_bytes(self):
        return sum(
            path.stat().st_size for path in self.output.glob("*.part") if path.is_file()
        )

    def _check_storage(self):
        if self._output_bytes() >= self.settings.max_output_gib * 1024**3:
            raise RuntimeError(
                "Output size limit reached. The partial trajectory has been preserved."
            )
        if (
            shutil.disk_usage(self.output).free
            < self.settings.reserve_free_gib * 1024**3
        ):
            raise RuntimeError(
                "Free disk reserve reached. The partial trajectory has been preserved."
            )

    def _atomic_json(self, path, value):
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
        temporary.replace(path)

    def status(self, state, error=None):
        elapsed = time.perf_counter() - self.started
        remaining = (
            elapsed * (self.config.duration_s / self.current_time - 1)
            if self.current_time > 0
            else None
        )
        value = {
            "status": state,
            "pid": os.getpid(),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
            "requested_duration_s": self.config.duration_s,
            "simulated_time_s": self.current_time,
            "simulated_days": self.current_time / 86400,
            "last_recorded_time_s": self.last_record_nanos * 1e-9
            if self.samples
            else None,
            "elapsed_wall_s": elapsed,
            "estimated_remaining_wall_s": max(0.0, remaining)
            if remaining is not None
            else None,
            "recorded_samples": self.samples,
            "collision_episodes": self.coupling.contact.total_episodes,
            "partial_output_bytes": self._output_bytes(),
            "error": error,
        }
        self._atomic_json(self.output / "run_status.json", value)
        return value

    def UpdateState(self, current_nanos):
        self.current_time = current_nanos * macros.NANO2SEC
        contact = self.coupling.contact
        if self.current_time <= self.config.dense_duration_s:
            interval = self.settings.initial_s
        elif (
            self.current_time
            - max(contact.last_impact_time, self.coupling.last_dynamic_time)
            < 2.0
        ):
            interval = self.settings.active_s
        else:
            interval = self.settings.quiet_s
        due = current_nanos - self.last_record_nanos >= macros.sec2nano(interval)
        new_episode = contact.total_episodes != self.last_seen_episode
        if due or new_episode or current_nanos == self.end_nanos:
            self._sample(current_nanos)
        if self.current_time >= self.next_storage_check:
            self._check_storage()
            self.next_storage_check = self.current_time + 60
        if self.current_time >= self.next_progress:
            self.csv_file.flush()
            self.events_file.flush()
            status = self.status("running")
            eta = status["estimated_remaining_wall_s"]
            suffix = f", ETA {eta / 60:.1f} min" if eta is not None else ""
            print(
                f"  {self.current_time / 3600:.2f} / {self.config.duration_s / 3600:.2f} h, "
                f"{contact.total_episodes} contacts, {self.samples:,} samples{suffix}",
                flush=True,
            )
            self.next_progress = self.current_time + self.settings.progress_s

    def finish(self, completed, error=None):
        if (
            completed
            and self.coupling.states is not None
            and self.last_record_nanos < round(self.current_time * 1e9)
        ):
            if np.all(np.isfinite(self.coupling.states)):
                self._sample(round(self.current_time * 1e9))
        self._drain_events(final=True)
        self.csv_file.close()
        self.events_file.close()
        # Releasing the unregistered native module flushes and closes its file.
        self.viz = None
        state = "completed" if completed else "interrupted"
        contact = self.coupling.contact
        summary = {
            "status": state,
            "error": error,
            "basilisk_version": basilisk_version,
            "config": asdict(self.config),
            "recording": asdict(self.settings),
            "environment": "Earth J2 and live per-bus atmospheric drag"
            if self.coupling.drag
            else "Earth J2",
            "orbit": self.orbit.summary(),
            "drag": self.coupling.drag.summary() if self.coupling.drag else None,
            "release_time_s": 0.0,
            "continuous_run": {
                "duration_s": self.current_time,
                "requested_duration_s": self.config.duration_s,
                "design_orbits": self.current_time / self.orbit.period_s,
                "minimum_recorded_com_altitude_m": self.min_altitude,
                "maximum_recorded_com_altitude_m": self.max_altitude,
                "single_trajectory_for_all_views": True,
            },
            "scenarios": [
                {
                    "name": "Continuous orbital separation and tether dynamics",
                    "duration_s": self.current_time,
                    "first_recorded_taut_s": self.first_taut,
                    "collision_episodes": contact.total_episodes,
                    "contact_statistics": {
                        "impulse_count": contact.total_impulses,
                        "maximum_penetration_m": contact.maximum_penetration_m,
                        "kinetic_energy_lost_j": contact.total_energy_lost_j,
                    },
                    "maximum_recorded_attachment_separation_m": self.max_gap,
                    "maximum_recorded_center_separation_m": self.max_centers,
                    "maximum_recorded_tension_n": self.max_tension,
                    "final_relative_mechanical_energy_j": self.final_energy,
                }
            ],
            "collision_events_file": "collision_events.jsonl"
            if completed
            else "collision_events.jsonl.part",
            "logged_collision_episodes": self.logged_events,
            "first_collision_event": self.first_event,
            "last_collision_event": self.last_event,
            "initial_hub_states": self.initial_states.tolist()
            if self.initial_states is not None
            else None,
            "final_hub_states": self.last_states.tolist()
            if self.last_states is not None
            else None,
            "notes": [
                "Both native spacecraft are integrated continuously. No repeated clips, frozen relative poses or orbital substitution.",
                "Collision detection and tension-only tether forces remain active for the entire run.",
                "Only recording cadence changes. New contact episode starts are recorded exactly.",
                "The visible slack tether shape is schematic. Transverse tether dynamics are omitted.",
            ],
        }
        if self.coupling.drag:
            summary["drag"]["energy_equivalent_semimajor_axis_change_m"] = (
                2
                * self.orbit.radius_m**2
                / EARTH_MU
                * self.coupling.drag.work_j
                / (2 * self.config.mass_kg)
            )
        if completed:
            for name in ("mission.bin", "mission.csv", "collision_events.jsonl"):
                (self.output / (name + ".part")).replace(self.output / name)
            self._atomic_json(self.output / "results.json", summary)
        else:
            self._atomic_json(self.output / "partial_results.json", summary)
        self.status(state, error)
        return summary


def run_streaming(
    config,
    orbit,
    output,
    drag=None,
    settings=StreamSettings(),
    open_result=False,
    app=None,
):
    if orbit is None:
        raise ValueError("Streaming mission mode requires an Earth orbit")
    settings.validate(config)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    status_path = output / "run_status.json"
    if status_path.exists():
        previous = json.loads(status_path.read_text())
        if previous.get("status") == "running":
            try:
                os.kill(previous["pid"], 0)
            except ProcessLookupError:
                pass
            else:
                raise RuntimeError(
                    f"A mission run is already active (PID {previous['pid']})"
                )
    if shutil.disk_usage(output).free < settings.reserve_free_gib * 1024**3:
        raise RuntimeError("Insufficient free disk space for the configured reserve")
    sim, _, coupling, _ = build_simulation(config, orbit, drag)
    recorder = MissionRecorder(sim, coupling, config, orbit, output, settings)
    coupling.next_report = float("inf")
    sim.AddModelToTask("dynamics", recorder, 5)
    try:
        sim.InitializeSimulation()
        sim.ConfigureStopTime(macros.sec2nano(config.duration_s))
        sim.ExecuteSimulation()
    except BaseException as error:
        recorder.finish(False, f"{type(error).__name__}: {error}")
        raise
    summary = recorder.finish(True)
    print(
        f"Completed {config.duration_s / 86400:g} days: {output / 'mission.bin'}",
        flush=True,
    )
    if open_result:
        open_vizard(output / "mission.bin", app)
    return summary
