"""Compact Vizard comparison of mean circular orbits at lifetime milestones.

All milestones use the initial orbital plane to make radius differences clear.
Each milestone uses two 1.5U buses joined by a deployed tether. This is fixed
relative geometry for GUI inspection. Deployment dynamics remain in mission.bin.
"""

from pathlib import Path

import numpy as np
from Basilisk.architecture import messaging
from Basilisk.simulation import vizInterface
from Basilisk.utilities import (
    RigidBodyKinematics as rbk,
    SimulationBaseClass,
    macros,
    vizSupport,
)

from geometry import tether_nodes
from lifetime import YEAR_S
from orbit_environment import EARTH_MU, EARTH_RADIUS_M, body_frame
from simulate import Config
from vizard_scene import (
    PlanetMessages,
    SEGMENTS,
    configure_deployment_models,
    deployment_names,
)


COLORS = ([35, 139, 69, 255], [33, 113, 181, 255], [203, 24, 29, 255])


def comparison_milestones(result, config, orbit):
    candidates = (
        ("Launch", 0.0),
        ("Mission_end", config.mission_s),
        ("Post_mission_end", config.duration_s),
    )
    milestones = []
    for label, time in candidates:
        altitude = result.altitude_at(time)
        if altitude is not None:
            name = f"{label}_{time / YEAR_S:g}y_{altitude / 1000:.1f}km"
            milestones.append((name, altitude))
    if result.threshold_time_s is not None:
        name = f"Stop_boundary_{result.threshold_time_s / YEAR_S:.2f}y_{config.reentry_altitude_m / 1000:g}km"
        milestones.append((name, config.reentry_altitude_m))
    return milestones


def circular_state(altitude_m, inclination_rad, raan_rad, time_s, phase_rad=0.0):
    radius = EARTH_RADIUS_M + altitude_m
    rate = np.sqrt(EARTH_MU / radius**3)
    phase = rate * time_s + phase_rad
    x = np.array([np.cos(raan_rad), np.sin(raan_rad), 0.0])
    y = np.array(
        [
            -np.sin(raan_rad) * np.cos(inclination_rad),
            np.cos(raan_rad) * np.cos(inclination_rad),
            np.sin(inclination_rad),
        ]
    )
    position = radius * (np.cos(phase) * x + np.sin(phase) * y)
    velocity = radius * rate * (-np.sin(phase) * x + np.cos(phase) * y)
    return position, velocity


class TetheredPair:
    """Physical display dimensions with a shared Vizard parent for all parts."""

    def __init__(self, name, config):
        self.name, self.config = name, config
        self.prefix = f"{name}_"
        bodies, segments = deployment_names(self.prefix)
        self.frame_msg = messaging.SCStatesMsg()
        self.component_msgs = [messaging.SCStatesMsg() for _ in bodies + segments]
        self.objects = [(name, self.frame_msg)] + list(
            zip(bodies + segments, self.component_msgs)
        )
        separation = config.tether_length_m + config.body_length_m
        buses = np.array([[-separation / 2, 0, 0], [separation / 2, 0, 0]])
        nodes = tether_nodes(config.tether_length_m, config.tether_length_m, SEGMENTS)
        self.offsets = np.vstack([buses, (nodes[:-1] + nodes[1:]) / 2])

    def configure(self, viz, color):
        for name, message in self.objects:
            entry = vizInterface.VizSpacecraftData()
            entry.spacecraftName = name
            if name == self.name:
                entry.spacecraftSprite = vizSupport.setSprite("CIRCLE", list(color))
                entry.oscOrbitLineColor = vizInterface.IntVector(color)
            else:
                entry.parentSpacecraftName = self.name
                entry.oscOrbitLineColor = vizInterface.IntVector([0, 0, 0, 0])
            entry.scStateInMsg.subscribeTo(message)
            viz.scData.push_back(entry)
        configure_deployment_models(viz, self.config, self.name, self.prefix, color)

    def update(self, position, velocity, nanos):
        rotation = body_frame(position, velocity)
        sigma = rbk.C2MRP(rotation.T).tolist()
        omega = np.cross(position, velocity) / np.dot(position, position)
        for message, offset in [
            (self.frame_msg, np.zeros(3)),
            *zip(self.component_msgs, self.offsets),
        ]:
            arm = rotation @ offset
            payload = messaging.SCStatesMsgPayload()
            payload.r_BN_N = (position + arm).tolist()
            payload.v_BN_N = (velocity + np.cross(omega, arm)).tolist()
            payload.sigma_BN = sigma
            payload.omega_BN_B = (rotation.T @ omega).tolist()
            message.write(payload, nanos)


def export_comparison(result, config, orbit, path: Path, step_s=20.0):
    if not vizSupport.vizFound:
        raise RuntimeError("This Basilisk build does not include Vizard support")
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    sim = SimulationBaseClass.SimBaseClass()
    process = sim.CreateNewProcess("lifetime_comparison")
    process.addTask(sim.CreateNewTask("comparison", macros.sec2nano(step_s)))
    viz = vizInterface.VizInterface()
    viz.ModelTag = "mean_orbit_milestone_comparison"
    viz.saveFile, viz.protoFilename = True, str(path)
    viz.settings = vizInterface.VizSettings()
    for name in ("customModelList", "stdCameraList", "pointLineList", "targetLineList"):
        getattr(vizSupport, name).clear()
    viz.settings.ambient = 0.4
    viz.settings.spacecraftShadowBrightness = 0.5
    viz.settings.spacecraftSizeMultiplier = 1.0
    viz.settings.mainCameraTarget = "earth"
    viz.settings.forceStartAtSpacecraftLocalView = -1
    viz.settings.orbitLinesOn = 1
    viz.settings.trueTrajectoryLinesOn = -1
    viz.settings.showSpacecraftAsSprites = -1
    viz.settings.showSpacecraftLabels = 1
    viz.settings.spacecraftCSon = -1
    viz.settings.viewCameraViewHUD = -1
    viz.liveSettings.playbackInRealTime = 1
    # Vizard defines this setting as an exponent: playback speed is 2**7.
    viz.liveSettings.playbackMultiplier = 7
    milestones = comparison_milestones(result, config, orbit)
    pairs = []
    for name, _ in milestones:
        pair = TetheredPair(name, Config(mass_kg=config.mass_kg / 2))
        pairs.append(pair)
        color = (
            COLORS[0]
            if name.startswith("Launch")
            else COLORS[1]
            if name.startswith("Mission_end")
            else COLORS[2]
        )
        pair.configure(viz, color)
    planets = PlanetMessages(orbit)
    bodies = []
    for name, mu, radius in (
        ("earth", EARTH_MU, EARTH_RADIUS_M),
        ("sun", 1.3271244e20, 695700000.0),
    ):
        body = vizInterface.GravBodyInfo()
        body.bodyName = body.modelDictionaryKey = name
        body.mu, body.radEquator, body.radiusRatio = mu, radius, 1.0
        bodies.append(body)
    viz.gravBodyInformation = vizInterface.GravBodyInfoVector(bodies)
    viz.spiceInMsgs = messaging.SpicePlanetStateMsgInMsgsVector(
        [message.addSubscriber() for message in planets.messages]
    )
    epoch = messaging.EpochMsgPayload()
    epoch.year, epoch.month, epoch.day = (
        orbit.epoch.year,
        orbit.epoch.month,
        orbit.epoch.day,
    )
    epoch.hours, epoch.minutes, epoch.seconds = (
        orbit.epoch.hour,
        orbit.epoch.minute,
        float(orbit.epoch.second),
    )
    epoch_msg = messaging.EpochMsg().write(epoch)
    viz.epochInMsg.subscribeTo(epoch_msg)
    sim.AddModelToTask("comparison", viz)
    sim.InitializeSimulation()
    end_nanos = macros.sec2nano(orbit.period_s)
    times = np.r_[
        np.rint(np.arange(0, orbit.period_s, step_s) * 1e9).astype(np.int64), end_nanos
    ]
    times = np.unique(times)
    times = times[(times >= 0) & (times <= end_nanos)]
    print(f"Encoding {len(times) - 1:,} lifetime comparison frames...", flush=True)
    for nanos in times:
        nanos = int(nanos)
        time = nanos * macros.NANO2SEC
        planets.update(time, nanos, 0)
        for i, (pair, (_, altitude)) in enumerate(zip(pairs, milestones)):
            # These are comparison orbits. Separate marker phases keep their
            # labels readable without changing the physical orbit radii.
            position, velocity = circular_state(
                altitude,
                orbit.inclination_rad,
                np.deg2rad(orbit.raan_deg),
                time,
                phase_rad=2 * np.pi * i / len(milestones),
            )
            pair.update(position, velocity, nanos)
        viz.UpdateState(nanos)
    return path
