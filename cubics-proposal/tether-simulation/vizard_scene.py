"""One continuous Vizard scene with an orbit view and a synchronized close-up."""

from pathlib import Path
import platform
import subprocess

import numpy as np
from Basilisk.architecture import messaging, sysModel
from Basilisk.simulation import vizInterface
from Basilisk.utilities import (
    RigidBodyKinematics as rbk,
    SimulationBaseClass,
    macros,
    vizSupport,
)

from geometry import tether_nodes
from fast_scene import segment_poses
from orbit_environment import (
    EARTH_MU,
    EARTH_RADIUS_M,
    body_frame,
    earth_rotation,
    frame_from_x,
    sun_position,
)

SEGMENTS = 32
DISPLAY_DIAMETER_M = 0.004
FRAME_NAME = "Deployment_center"
# Only the gravity free regression view uses this display translation.
DISPLAY_ORIGIN = np.array([0.0, 0.0, 10.0])
DISPLAY_VELOCITY = np.array([0.0, 1.0, 0.0])


def sample_array(time, times, array):
    i = int(np.clip(np.searchsorted(times, time) - 1, 0, len(times) - 2))
    f = np.clip((time - times[i]) / (times[i + 1] - times[i]), 0.0, 1.0)
    return array[i] + f * (array[i + 1] - array[i])


def sample_attitude(time, times, values):
    i = int(np.clip(np.searchsorted(times, time) - 1, 0, len(times) - 2))
    f = np.clip((time - times[i]) / (times[i + 1] - times[i]), 0.0, 1.0)
    q0, q1 = rbk.MRP2EP(values[i]), rbk.MRP2EP(values[i + 1])
    if np.dot(q0, q1) < 0:
        q1 = -q1
    quaternion = (1 - f) * q0 + f * q1
    quaternion /= np.linalg.norm(quaternion)
    return rbk.EP2MRP(quaternion)


class PlanetMessages:
    def __init__(self, orbit):
        self.orbit = orbit
        self.messages = [
            messaging.SpicePlanetStateMsg(),
            messaging.SpicePlanetStateMsg(),
        ]
        self.payloads = [
            messaging.SpicePlanetStateMsgPayload(),
            messaging.SpicePlanetStateMsgPayload(),
        ]
        for name, payload in zip(("earth", "sun"), self.payloads):
            payload.PlanetName = name
            payload.J20002Pfix = np.eye(3).tolist()

    def update(self, time, nanos, module_id):
        earth, sun = self.payloads
        if self.orbit:
            earth.PositionVector = [0.0, 0.0, 0.0]
            earth.J20002Pfix = earth_rotation(self.orbit, time)
            sun.PositionVector = sun_position(self.orbit, time).tolist()
        else:
            earth.PositionVector = [0.0, 0.0, -1e9]
            sun.PositionVector = [1.5e11, 0.0, 0.0]
        for message, payload in zip(self.messages, self.payloads):
            message.write(payload, nanos, module_id)


class LiveScene:
    """Publish the actual hub states without retaining a trajectory in memory."""

    def __init__(self, config, orbit):
        self.config, self.orbit = config, orbit
        self.planets = PlanetMessages(orbit)
        self.frame_msg = messaging.SCStatesMsg()
        self.bus_msgs = [[messaging.SCStatesMsg(), messaging.SCStatesMsg()]]
        self.segment_msgs = [[messaging.SCStatesMsg() for _ in range(SEGMENTS)]]

    def write(self, states, nanos):
        time = nanos * macros.NANO2SEC
        self.planets.update(time, nanos, 0)
        positions, velocities = states[:, :3], states[:, 3:6]
        center, velocity = positions.mean(axis=0), velocities.mean(axis=0)
        view = body_frame(center, velocity)
        payload = messaging.SCStatesMsgPayload()
        payload.r_BN_N, payload.v_BN_N = center.tolist(), velocity.tolist()
        payload.sigma_BN = rbk.C2MRP(view.T).tolist()
        self.frame_msg.write(payload, nanos)
        anchors, anchor_v = [], []
        for bus, message in enumerate(self.bus_msgs[0]):
            payload = messaging.SCStatesMsgPayload()
            payload.r_BN_N, payload.v_BN_N = (
                positions[bus].tolist(),
                velocities[bus].tolist(),
            )
            payload.sigma_BN, payload.omega_BN_B = (
                states[bus, 6:9].tolist(),
                states[bus, 9:12].tolist(),
            )
            message.write(payload, nanos)
            rotation = rbk.MRP2C(states[bus, 6:9]).T
            port = np.array([(0.5 - bus) * self.config.body_length_m, 0.0, 0.0])
            anchors.append(positions[bus] + rotation @ port)
            anchor_v.append(
                velocities[bus] + rotation @ np.cross(states[bus, 9:12], port)
            )
        anchors, anchor_v = np.array(anchors), np.array(anchor_v)
        delta = anchors[1] - anchors[0]
        gap = np.linalg.norm(delta)
        direction = delta / gap if gap > 1e-7 else view[:, 0]
        tether_frame = frame_from_x(direction, view[:, 2])
        curve = tether_nodes(gap, self.config.tether_length_m, SEGMENTS)
        nodes = (
            anchors.mean(axis=0)
            + curve[:, :1] * direction
            + curve[:, 1:2] * tether_frame[:, 2]
        )
        centers, attitudes = segment_poses(nodes, view[:, 2])
        for message, center, attitude in zip(self.segment_msgs[0], centers, attitudes):
            payload = messaging.SCStatesMsgPayload()
            payload.r_BN_N = center.tolist()
            payload.v_BN_N = velocity.tolist()
            payload.sigma_BN = attitude.tolist()
            message.write(payload, nanos)
        speed = float(np.dot(delta, anchor_v[1] - anchor_v[0]) / max(gap, 1e-12))
        return anchors, gap, speed


class SceneReplay(sysModel.SysModel):
    def __init__(self, results, config, offsets):
        super().__init__()
        self.ModelTag = "recorded_deployment_to_vizard"
        self.results, self.config, self.offsets = results, config, offsets
        self.orbit = results[0].orbit
        self.center_positions = results[0].positions.mean(axis=1)
        self.center_velocities = results[0].velocities.mean(axis=1)
        self.planets = PlanetMessages(self.orbit)
        self.frame_msg = messaging.SCStatesMsg()
        self.bus_msgs = [
            [messaging.SCStatesMsg(), messaging.SCStatesMsg()] for _ in results
        ]
        self.segment_msgs = [
            [messaging.SCStatesMsg() for _ in range(SEGMENTS)] for _ in results
        ]

    def UpdateState(self, current_nanos):
        time = current_nanos * macros.NANO2SEC
        self.planets.update(time, current_nanos, self.moduleID)
        result = self.results[0]
        if self.orbit:
            origin = sample_array(time, result.time, self.center_positions)
            velocity = sample_array(time, result.time, self.center_velocities)
            view = body_frame(origin, velocity)
        else:
            origin = DISPLAY_ORIGIN + time * DISPLAY_VELOCITY
            velocity = DISPLAY_VELOCITY
            view = np.eye(3)
        center = messaging.SCStatesMsgPayload()
        center.r_BN_N, center.v_BN_N = origin.tolist(), velocity.tolist()
        center.sigma_BN = rbk.C2MRP(view.T).tolist()
        self.frame_msg.write(center, current_nanos, self.moduleID)
        for i, (result, offset) in enumerate(zip(self.results, self.offsets)):
            anchors = []
            for bus in range(2):
                payload = messaging.SCStatesMsgPayload()
                position = sample_array(time, result.time, result.positions[:, bus])
                speed = sample_array(time, result.time, result.velocities[:, bus])
                if self.orbit:
                    sigma = sample_attitude(time, result.time, result.attitudes[:, bus])
                    payload.sigma_BN = sigma.tolist()
                    rotation = rbk.MRP2C(sigma).T
                    payload.omega_BN_B = sample_array(
                        time, result.time, result.angular_velocities[:, bus]
                    ).tolist()
                else:
                    position += origin + offset
                    speed += velocity
                    rotation = np.eye(3)
                payload.r_BN_N, payload.v_BN_N = position.tolist(), speed.tolist()
                self.bus_msgs[i][bus].write(payload, current_nanos, self.moduleID)
                port = np.array([(0.5 - bus) * self.config.body_length_m, 0.0, 0.0])
                anchors.append(position + rotation @ port)
            delta = anchors[1] - anchors[0]
            gap = np.linalg.norm(delta)
            direction = delta / gap if gap > 1e-7 else view[:, 0]
            # Put the schematic orbital slack loop in a plane visible from
            # the radial camera. This changes no attachment or dynamics state.
            plane_normal = view[:, 2] if self.orbit else view[:, 1]
            tether_frame = frame_from_x(direction, plane_normal)
            curve = tether_nodes(gap, self.config.tether_length_m, SEGMENTS)
            nodes = (
                (anchors[0] + anchors[1]) / 2
                + curve[:, :1] * direction
                + curve[:, 1:2] * tether_frame[:, 2]
            )
            for message, left, right in zip(
                self.segment_msgs[i], nodes[:-1], nodes[1:]
            ):
                rotation = frame_from_x(right - left, plane_normal)
                payload = messaging.SCStatesMsgPayload()
                payload.r_BN_N = ((left + right) / 2).tolist()
                payload.v_BN_N = velocity.tolist()
                payload.sigma_BN = rbk.C2MRP(rotation.T).tolist()
                message.write(payload, current_nanos, self.moduleID)


def setup_viz(sim, task, replay, objects, path, overview=False, register=True):
    viz = vizInterface.VizInterface()
    viz.ModelTag = "native_vizard_playback"
    viz.saveFile, viz.protoFilename = True, str(path)
    viz.settings = vizInterface.VizSettings()
    for name, message in objects:
        entry = vizInterface.VizSpacecraftData()
        entry.spacecraftName = name
        # Vizard must render the buses and tether in the same local assembly.
        # Independent spacecraft roots collapse together in the orbit-scale
        # instrument view, while parented components retain meter-scale offsets.
        # Keep the messages in ECI. Vizard computes each offset from the parent.
        if name != FRAME_NAME:
            entry.parentSpacecraftName = FRAME_NAME
        entry.scStateInMsg.subscribeTo(message)
        viz.scData.push_back(entry)
    bodies = []
    for name, mu, radius in (
        ("earth", EARTH_MU, EARTH_RADIUS_M),
        ("sun", 1.3271244e20, 695700000.0),
    ):
        info = vizInterface.GravBodyInfo()
        info.bodyName = info.modelDictionaryKey = name
        info.mu, info.radEquator, info.radiusRatio = mu, radius, 1.0
        bodies.append(info)
    viz.gravBodyInformation = vizInterface.GravBodyInfoVector(bodies)
    viz.spiceInMsgs = messaging.SpicePlanetStateMsgInMsgsVector(
        [m.addSubscriber() for m in replay.planets.messages]
    )
    if replay.orbit:
        epoch = replay.orbit.epoch
        payload = messaging.EpochMsgPayload()
        payload.year, payload.month, payload.day = epoch.year, epoch.month, epoch.day
        payload.hours, payload.minutes, payload.seconds = (
            epoch.hour,
            epoch.minute,
            float(epoch.second),
        )
        replay.epoch_message = messaging.EpochMsg().write(payload)
        viz.epochInMsg.subscribeTo(replay.epoch_message)
    if register:
        sim.AddModelToTask(task, viz, 0)
    for name in ("customModelList", "stdCameraList", "pointLineList", "targetLineList"):
        getattr(vizSupport, name).clear()
    viz.settings.orbitLinesOn = 1 if overview else -1
    viz.settings.trueTrajectoryLinesOn = 1 if overview else -1
    viz.settings.showSpacecraftAsSprites = -1
    viz.settings.showSpacecraftLabels = -1
    viz.settings.spacecraftCSon = -1
    viz.settings.ambient = 0.4
    viz.settings.spacecraftShadowBrightness = 0.5
    viz.settings.spacecraftSizeMultiplier = 1.0
    viz.settings.mainCameraTarget = "earth" if overview else FRAME_NAME
    viz.settings.forceStartAtSpacecraftLocalView = -1 if overview else 1
    viz.settings.messageBufferSize = (
        64 * 1024 * 1024 if replay.config.duration_s > 300 else -1
    )
    viz.liveSettings.playbackInRealTime = 1
    viz.liveSettings.playbackMultiplier = 0
    return viz


def deployment_names(prefix=""):
    return (
        [f"{prefix}CubeSat_A", f"{prefix}CubeSat_B"],
        [f"{prefix}Tether_{i:02d}" for i in range(SEGMENTS)],
    )


def deployment_objects(replay, frame_name=FRAME_NAME):
    bodies, segments = deployment_names()
    return (
        [(frame_name, replay.frame_msg)]
        + list(zip(bodies, replay.bus_msgs[0]))
        + list(zip(segments, replay.segment_msgs[0]))
    )


def configure_deployment_models(
    viz, config, frame_name=FRAME_NAME, prefix="", bus_color=None
):
    """Apply native cuboid models to a two-bus assembly and its tether."""
    bodies, segments = deployment_names(prefix)
    vizSupport.createCustomModel(
        viz,
        modelPath="CUBE",
        simBodiesToModify=[frame_name],
        scale=[0.004] * 3,
        color=[1, 1, 1, 255],
    )
    vizSupport.createCustomModel(
        viz,
        modelPath="CUBE",
        simBodiesToModify=bodies,
        scale=[config.body_length_m, config.body_width_m, config.body_height_m],
        color=bus_color if bus_color is not None else [65, 150, 210, 255],
    )
    vizSupport.createCustomModel(
        viz,
        modelPath="CUBE",
        simBodiesToModify=segments,
        scale=[
            config.tether_length_m / SEGMENTS * 1.01,
            DISPLAY_DIAMETER_M,
            DISPLAY_DIAMETER_M,
        ],
        color=[220, 230, 245, 255],
    )


def configure_deployment_view(viz, replay, frame_name=FRAME_NAME):
    configure_deployment_models(viz, replay.config, frame_name)
    viz.settings.viewCameraViewHUD = 1
    _, replay.camera_message = vizSupport.createCameraConfigMsg(
        viz,
        cameraID=1,
        parentName=frame_name,
        cameraPos_B=[0.0, -0.4, 4.8] if replay.orbit else [0.0, 4.8, -0.4],
        sigma_CB=[1.0, 0.0, 0.0]
        if replay.orbit
        else [float(np.tan(np.pi / 8)), 0.0, 0.0],
        fieldOfView=np.deg2rad(40),
        resolution=[1280, 720],
        renderRate=0.0,
        skyBox="",
        showHUDElementsInImage=-1,
    )


def visualization_times(result, config, fine_step_s=0.02, coarse_step_s=0.2):
    windows = [(0.0, min(config.duration_s, config.dense_duration_s))]
    active = np.flatnonzero(result.tension > 1e-3)
    if len(active):
        for group in np.split(active, np.flatnonzero(np.diff(active) > 1) + 1):
            windows.append(
                (
                    max(0.0, result.time[group[0]] - 0.5),
                    min(config.duration_s, result.time[group[-1]] + 0.5),
                )
            )
    for event in result.collision_events:
        windows.append(
            (
                max(0.0, event["time_s"] - 0.5),
                min(config.duration_s, event["end_time_s"] + 1.0),
            )
        )
    merged = []
    for lo, hi in sorted(windows):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
        else:
            merged.append((lo, hi))
    grids = [
        np.arange(0, config.duration_s, coarse_step_s),
        np.array([config.duration_s]),
    ]
    grids.extend(
        np.arange(lo, hi + fine_step_s * 0.1, fine_step_s) for lo, hi in merged
    )
    grids.extend(
        np.array([event["time_s"], event["end_time_s"]])
        for event in result.collision_events
    )
    times = np.unique(np.rint(np.concatenate(grids) * 1e9).astype(np.int64))
    return times[(times >= 0) & (times <= macros.sec2nano(config.duration_s))]


def export_vizard(results, config, path: Path, step_s=0.02):
    if not vizSupport.vizFound:
        raise RuntimeError("This Basilisk build does not include Vizard support")
    if len(results) != 1:
        raise ValueError("There is one deployment scenario, without braking")
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    sim = SimulationBaseClass.SimBaseClass()
    process = sim.CreateNewProcess("vizard_export")
    process.addTask(sim.CreateNewTask("vizard_playback", macros.sec2nano(step_s)))
    replay = SceneReplay(results, config, [np.zeros(3)])
    sim.AddModelToTask("vizard_playback", replay, 10)
    objects = deployment_objects(replay)
    viz = setup_viz(
        sim, "vizard_playback", replay, objects, path, overview=replay.orbit is not None
    )
    configure_deployment_view(viz, replay)
    sim.InitializeSimulation()
    times = visualization_times(results[0], config, fine_step_s=step_s)
    print(
        f"Encoding {len(times) - 1:,} native Vizard frames from the continuous run...",
        flush=True,
    )
    # No dynamics are integrated during this export. Each native module is
    # stepped at its packet timestamp, allowing sparse packets in quiet arcs.
    for i, nanos in enumerate(times):
        replay.UpdateState(int(nanos))
        viz.UpdateState(int(nanos))
        if len(times) > 10000 and i and i % (len(times) // 4) == 0:
            print(f"  Vizard export {100 * i // len(times)}%", flush=True)
    return path


def find_vizard():
    for path in (
        Path(__file__).parent / ".tools/Vizard.app",
        Path("/Applications/Vizard.app"),
        Path.home() / "Applications/Vizard.app",
    ):
        if path.exists():
            return path.resolve()
    return None


def open_vizard(path: Path, app: Path | None = None, description: str | None = None):
    app = app or find_vizard()
    if app is None:
        raise RuntimeError(
            "Download Vizard from https://avslab.github.io/basilisk/Vizard/VizardDownload.html or pass --vizard-app PATH"
        )
    print(f"Opening Vizard: {path.resolve()}", flush=True)
    print(
        description
        or "Orbit view and instrument close-up now share this one continuous timeline.",
        flush=True,
    )
    if platform.system() == "Darwin":
        subprocess.run(
            ["open", "-n", str(app), "--args", "-loadFile", str(path.resolve())],
            check=True,
        )
    else:
        subprocess.Popen([str(app), "-loadFile", str(path.resolve())])
