"""Attachment forces and torques for the orbital deployment case."""

import numpy as np
from Basilisk.architecture import sysModel
from Basilisk.utilities import RigidBodyKinematics as rbk

from orbit_environment import body_frame, earth_j2
from contact import CollisionResolver
from fast_forces import orbital_forces


def initialize_orbit(buses, config, orbit):
    position, velocity = orbit.initial_state()
    rotation = body_frame(position, velocity)
    normal = rotation[:, 1]
    omega_n = orbit.mean_motion_rad_s * normal
    earth = earth_j2()
    for i, bus in enumerate(buses):
        offset = (i - 0.5) * config.body_length_m * rotation[:, 0]
        bus.hub.r_CN_NInit = (position + offset).tolist()
        bus.hub.v_CN_NInit = (velocity + np.cross(omega_n, offset)).tolist()
        bus.hub.sigma_BNInit = rbk.C2MRP(rotation.T).tolist()
        bus.hub.omega_BN_BInit = (rotation.T @ omega_n).tolist()
        from Basilisk.simulation import spacecraft

        bus.gravField.gravBodies = spacecraft.GravBodyVector([earth])
    return earth


def attachment_state(payload, offset_b):
    rotation = rbk.MRP2C(payload.sigma_BN).T
    position = np.asarray(payload.r_BN_N) + rotation @ offset_b
    velocity = np.asarray(payload.v_BN_N) + rotation @ np.cross(
        payload.omega_BN_B, offset_b
    )
    return position, velocity, rotation


class OrbitCoupling(sysModel.SysModel):
    def __init__(self, buses, effectors, config, drag=None):
        super().__init__()
        self.ModelTag = "orbital_spring_tether_and_contact"
        self.buses, self.effectors, self.config = buses, effectors, config
        self.drag, self.states = drag, None
        self.spring_available = True
        self.contact = CollisionResolver(buses, config)
        inertia = np.asarray(buses[0].hub.IHubPntBc_B)
        self.parameters = np.array(
            [
                config.mass_kg,
                config.step_s,
                config.body_length_m,
                config.spring_stroke_m,
                config.spring_stiffness_n_m,
                config.tether_stiffness_n_m,
                config.tether_length_m,
                1 / inertia[1, 1],
                1 / inertia[2, 2],
            ]
        )
        self.last_dynamic_time = -1e30
        self.next_report = 600.0

    def UpdateState(self, current_nanos):
        time = current_nanos * 1e-9
        payloads = [bus.scStateOutMsg.read() for bus in self.buses]
        if not self.spring_available and self.contact.resolve(payloads, time):
            payloads = [bus.scStateOutMsg.read() for bus in self.buses]
        states = np.array(
            [[*p.r_BN_N, *p.v_BN_N, *p.sigma_BN, *p.omega_BN_B] for p in payloads]
        )
        self.states = states
        force_n, torques, self.spring_available, tension = orbital_forces(
            states, self.parameters, self.spring_available
        )
        if tension > 1e-3:
            self.last_dynamic_time = time
        forces = np.array([-force_n, force_n])
        if self.drag is not None:
            forces += self.drag.forces(states, time)
        self.effectors[0].extForce_N = forces[0].tolist()
        self.effectors[1].extForce_N = forces[1].tolist()
        for effector, torque in zip(self.effectors, torques):
            effector.extTorquePntB_B = torque.tolist()
        if time >= self.next_report:
            print(
                f"  Simulated {time / 60:.1f} / {self.config.duration_s / 60:.1f} min, {self.contact.total_episodes} contact episodes",
                flush=True,
            )
            self.next_report += 600.0


def record_geometry(positions, velocities, attitudes, angular_velocities, config):
    anchors = np.empty_like(positions)
    anchor_velocities = np.empty_like(velocities)
    for bus in range(2):
        offset = np.array([(0.5 - bus) * config.body_length_m, 0.0, 0.0])
        for i in range(len(positions)):
            rotation = rbk.MRP2C(attitudes[i, bus]).T
            anchors[i, bus] = positions[i, bus] + rotation @ offset
            anchor_velocities[i, bus] = velocities[i, bus] + rotation @ np.cross(
                angular_velocities[i, bus], offset
            )
    delta = anchors[:, 1] - anchors[:, 0]
    gap = np.linalg.norm(delta, axis=1)
    relative_v = anchor_velocities[:, 1] - anchor_velocities[:, 0]
    speed = np.sum(delta * relative_v, axis=1) / np.maximum(gap, 1e-12)
    return anchors, anchor_velocities, gap, speed
