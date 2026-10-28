"""Compiled attachment force calculation for a continuous full orbit run."""

import numpy as np
from numba import njit


@njit(cache=True)
def rotation_from_mrp(sigma):
    x, y, z = sigma
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    squared = np.dot(sigma, sigma)
    return (
        np.eye(3) + (8 * (skew @ skew) + 4 * (1 - squared) * skew) / (1 + squared) ** 2
    )


@njit(cache=True)
def orbital_forces(states, parameters, spring_available):
    mass, dt, length, stroke, ks, kt, rest_length, inv_iy, inv_iz = parameters
    rotations = np.empty((2, 3, 3))
    ports, port_v = np.empty((2, 3)), np.empty((2, 3))
    for b in range(2):
        rotation = rotation_from_mrp(states[b, 6:9])
        rotations[b] = rotation
        arm = (0.5 - b) * length
        ports[b] = states[b, :3] + arm * rotation[:, 0]
        local_v = np.array([0.0, states[b, 11] * arm, -states[b, 10] * arm])
        port_v[b] = states[b, 3:6] + rotation @ local_v
    delta, relative_v = ports[1] - ports[0], port_v[1] - port_v[0]
    gap = np.linalg.norm(delta)
    if gap >= stroke:
        spring_available = False
    if spring_available:
        direction = rotations[0][:, 0] + rotations[1][:, 0]
        direction /= np.linalg.norm(direction)
        gap = max(0.0, np.dot(delta, direction))
    else:
        direction = delta / gap if gap > 1e-10 else rotations[0][:, 0].copy()
    speed = np.dot(relative_v, direction)
    inverse_mass = 2 / mass
    for b in range(2):
        local_n = rotations[b].T @ direction
        arm = (0.5 - b) * length
        inverse_mass += arm**2 * (local_n[2] ** 2 * inv_iy + local_n[1] ** 2 * inv_iz)
    mu = 1 / inverse_mass
    force = 0.0
    for regime in range(3):
        if regime == 0:
            if not spring_available:
                continue
            stiffness, equilibrium = ks, stroke
        elif regime == 1:
            stiffness, equilibrium = 0.0, 0.0
        else:
            stiffness, equilibrium = kt, rest_length
        trial = (
            stiffness
            * (equilibrium - gap - 0.5 * speed * dt)
            / (1 + 0.25 * stiffness * dt**2 / mu)
        )
        middle_gap = gap + 0.5 * speed * dt + 0.25 * trial * dt**2 / mu
        in_spring = spring_available and middle_gap < stroke
        in_tether = middle_gap > rest_length
        if (
            (regime == 0 and in_spring)
            or (regime == 1 and not in_spring and not in_tether)
            or (regime == 2 and in_tether)
        ):
            force = trial
            break
    middle_delta = delta + 0.5 * dt * relative_v
    if not spring_available and np.linalg.norm(middle_delta) > 1e-7:
        direction = middle_delta / np.linalg.norm(middle_delta)
    force_n = force * direction
    torques = np.zeros((2, 3))
    for b in range(2):
        sign = -1 if b == 0 else 1
        local_f = rotations[b].T @ (sign * force_n)
        arm = (0.5 - b) * length
        torques[b, 1], torques[b, 2] = -arm * local_f[2], arm * local_f[1]
    return force_n, torques, spring_available, max(0.0, -force)
