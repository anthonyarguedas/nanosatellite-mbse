"""Frictionless rigid cuboid contact with normal restitution.

This is a single contact approximation, without structural damage or friction.
The collision impulse changes the live Basilisk states. It never relatches the
spacecraft, restarts the release spring, or changes their common orbit.
"""

from dataclasses import dataclass

import numpy as np
from numba import njit
from Basilisk.utilities import RigidBodyKinematics as rbk


@njit(cache=True)
def _dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


@njit(cache=True)
def _support(center, rotation, half, direction):
    point = center.copy()
    for k in range(3):
        projection = _dot3(rotation[:, k], direction)
        sign = 1.0 if projection > 1e-10 else (-1.0 if projection < -1e-10 else 0.0)
        point += sign * half[k] * rotation[:, k]
    return point


@njit(cache=True)
def _closest_segments(p1, q1, p2, q2):
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, b = np.dot(d1, d1), np.dot(d2, d2), np.dot(d1, d2)
    c, f = np.dot(d1, r), np.dot(d2, r)
    denominator = a * e - b * b
    s = (
        min(1.0, max(0.0, (b * f - c * e) / denominator))
        if denominator > 1e-18
        else 0.0
    )
    t = (b * s + f) / e
    if t < 0.0:
        t, s = 0.0, min(1.0, max(0.0, -c / a))
    elif t > 1.0:
        t, s = 1.0, min(1.0, max(0.0, (b - c) / a))
    return p1 + s * d1, p2 + t * d2


@njit(cache=True)
def _obb_contact(positions, rotations, half):
    delta = positions[1] - positions[0]
    axes = np.zeros((15, 3))
    axes[:3] = rotations[0].T
    axes[3:6] = rotations[1].T
    for i in range(3):
        for j in range(3):
            axes[6 + 3 * i + j] = np.cross(rotations[0][:, i], rotations[1][:, j])
    penetration, selected = 1e30, -1
    normal = np.zeros(3)
    for index in range(15):
        length = np.linalg.norm(axes[index])
        if length < 1e-9:
            continue
        axis = axes[index] / length
        radius = 0.0
        for body in range(2):
            for k in range(3):
                radius += half[k] * abs(_dot3(axis, rotations[body][:, k]))
        overlap = radius - abs(np.dot(delta, axis))
        if overlap < -1e-9:
            return False, 0.0, normal, np.zeros(3)
        # Prefer a face normal when an equivalent edge axis differs by roundoff.
        if overlap < penetration - 1e-9:
            penetration, selected = max(overlap, 0.0), index
            normal = axis if np.dot(delta, axis) >= 0 else -axis
    if selected < 3:
        b = _support(positions[1], rotations[1], half, -normal)
        local = rotations[0].T @ (b - positions[0])
        local = np.minimum(half, np.maximum(-half, local))
        local[selected] = half[selected] * (
            1 if _dot3(rotations[0][:, selected], normal) >= 0 else -1
        )
        a = positions[0] + rotations[0] @ local
    elif selected < 6:
        k = selected - 3
        a = _support(positions[0], rotations[0], half, normal)
        local = rotations[1].T @ (a - positions[1])
        local = np.minimum(half, np.maximum(-half, local))
        local[k] = half[k] * (1 if _dot3(rotations[1][:, k], -normal) >= 0 else -1)
        b = positions[1] + rotations[1] @ local
    else:
        i, j = (selected - 6) // 3, (selected - 6) % 3
        ca, cb = positions[0].copy(), positions[1].copy()
        for k in range(3):
            if k != i:
                ca += (
                    half[k]
                    * (1 if _dot3(rotations[0][:, k], normal) >= 0 else -1)
                    * rotations[0][:, k]
                )
            if k != j:
                cb += (
                    half[k]
                    * (1 if _dot3(rotations[1][:, k], -normal) >= 0 else -1)
                    * rotations[1][:, k]
                )
        ea, eb = half[i] * rotations[0][:, i], half[j] * rotations[1][:, j]
        a, b = _closest_segments(ca - ea, ca + ea, cb - eb, cb + eb)
    return True, penetration, normal, (a + b) / 2


@dataclass
class Contact:
    penetration: float
    normal: np.ndarray  # from A to B
    point: np.ndarray


def box_contact(positions, rotations, half):
    hit, depth, normal, point = _obb_contact(
        np.asarray(positions), np.asarray(rotations), np.asarray(half)
    )
    return Contact(depth, normal, point) if hit else None


def normal_impulse(
    positions,
    velocities,
    rotations,
    angular_velocities,
    inertia,
    mass,
    contact,
    restitution,
):
    velocities = np.array(velocities, dtype=float, copy=True)
    omega = np.array(angular_velocities, dtype=float, copy=True)
    arms = contact.point - positions
    world_omega = np.einsum("bij,bj->bi", rotations, omega)
    contact_v = velocities + np.cross(world_omega, arms)
    normal_speed = float(np.dot(contact_v[1] - contact_v[0], contact.normal))
    if normal_speed >= 0:
        return velocities, omega, 0.0, normal_speed, 0.0
    inv_i = 1 / np.diag(inertia)
    inverse_mass = 2 / mass
    for b in range(2):
        lever = np.cross(rotations[b].T @ arms[b], rotations[b].T @ contact.normal)
        inverse_mass += np.dot(lever * inv_i, lever)
    impulse = -(1 + restitution) * normal_speed / inverse_mass
    for b, sign in enumerate((-1, 1)):
        j = sign * impulse * contact.normal
        velocities[b] += j / mass
        omega[b] += inv_i * np.cross(rotations[b].T @ arms[b], rotations[b].T @ j)
    loss = 0.5 * (1 - restitution**2) * normal_speed**2 / inverse_mass
    return velocities, omega, float(impulse), normal_speed, float(loss)


class CollisionResolver:
    def __init__(self, buses, config):
        self.buses, self.config = buses, config
        self.half = (
            np.array([config.body_length_m, config.body_width_m, config.body_height_m])
            / 2
        )
        self.bound_squared = float((2 * np.linalg.norm(self.half) + 1e-6) ** 2)
        self.inertia = np.asarray(buses[0].hub.IHubPntBc_B)
        self.events = []
        self.last_impact_time = -1e30
        self.maximum_penetration_m = 0.0
        self.total_energy_lost_j = 0.0
        self.total_impulses = 0
        self.total_episodes = 0
        self.handles = None

    def resolve(self, payloads, time):
        positions = np.array([p.r_BN_N for p in payloads])
        delta = positions[1] - positions[0]
        if np.dot(delta, delta) > self.bound_squared:
            return False
        rotations = np.array([rbk.MRP2C(p.sigma_BN).T for p in payloads])
        contact = box_contact(positions, rotations, self.half)
        if contact is None:
            return False
        self.maximum_penetration_m = max(
            self.maximum_penetration_m, contact.penetration
        )
        v, omega, impulse, normal_speed, loss = normal_impulse(
            positions,
            np.array([p.v_BN_N for p in payloads]),
            rotations,
            np.array([p.omega_BN_B for p in payloads]),
            self.inertia,
            self.config.mass_kg,
            contact,
            self.config.restitution,
        )
        correction = max(0.0, contact.penetration - 1e-7)
        if correction == 0 and impulse == 0:
            return False
        positions[0] -= 0.5 * correction * contact.normal
        positions[1] += 0.5 * correction * contact.normal
        if self.handles is None:
            self.handles = [
                (
                    b.dynManager.getStateObject(b.hub.nameOfHubPosition),
                    b.dynManager.getStateObject(b.hub.nameOfHubVelocity),
                    b.dynManager.getStateObject(b.hub.nameOfHubOmega),
                )
                for b in self.buses
            ]
        nanos = int(round(time * 1e9))
        for b, bus in enumerate(self.buses):
            for handle, value in zip(self.handles[b], (positions[b], v[b], omega[b])):
                handle.setState(value.reshape(3, 1).tolist())
            # The central body is fixed at the ECI origin. Refresh message
            # properties as well as integration states, before logging.
            bus.dynManager.setPropertyValue(
                bus.gravField.inertialPositionPropName,
                positions[b].reshape(3, 1).tolist(),
            )
            bus.dynManager.setPropertyValue(
                bus.gravField.inertialVelocityPropName, v[b].reshape(3, 1).tolist()
            )
            bus.writeOutputStateMessages(nanos)
        if impulse > 0:
            self.total_impulses += 1
            self.total_energy_lost_j += loss
            if abs(normal_speed) > 1e-4:
                self.last_impact_time = time
            if self.events and time - self.events[-1]["end_time_s"] < 0.2:
                event = self.events[-1]
                event["end_time_s"] = time
                event["impulse_count"] += 1
                event["energy_lost_j"] += loss
                event["peak_impulse_n_s"] = max(event["peak_impulse_n_s"], impulse)
            else:
                self.total_episodes += 1
                self.events.append(
                    {
                        "time_s": time,
                        "end_time_s": time,
                        "impulse_count": 1,
                        "energy_lost_j": loss,
                        "peak_impulse_n_s": impulse,
                        "initial_normal_speed_m_s": normal_speed,
                    }
                )
        return True
