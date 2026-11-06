#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scipy>=1.13", "matplotlib>=3.8"]
# ///

# %% Imports
from __future__ import annotations

from dataclasses import dataclass, replace
from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import approx_fprime

# %% Material assumptions and parameters
# Illustrative effective moduli for sensitivity studies, not product specifications.
# Replace these with measurements for the selected grade, braid, and terminations.
MATERIAL_YOUNGS_MODULUS_PA = {
    "Nylon": 2.0e9,
    "Dyneema": 100.0e9,
}
TETHER_LENGTHS_M = (2.0, 200.0)


@dataclass(frozen=True)
class Parameters:
    mass_1_kg: float = 1.25
    mass_2_kg: float = 1.25
    altitude_m: float = 600_000.0
    earth_radius_m: float = 6_378_137.0
    earth_mu_m3_s2: float = 3.986004418e14
    gravity_enabled: bool = True

    initial_separation_m: float = 0.101
    initial_direction_rtn: tuple[float, float, float] = (1.0, 0.0, 0.0)
    initial_separation_speed_m_s: float = 0.0
    initial_pair_spin_rad_s: float = 0.0  # Extra rotation about orbit normal, in RTN.
    collision_distance_m: float = 0.10  # Approximate centre separation at contact.

    spring_stiffness_N_m: float = 500.0
    spring_stroke_m: float = 0.02  # Initial compression and available push distance.

    initial_free_length_m: float = 0.15  # Unstretched length already outside reel.
    total_tether_length_m: float = 2.0  # Includes initial_free_length_m.
    tether_youngs_modulus_Pa: float = 2.0e9
    tether_diameter_m: float = 0.0004  # Equivalent circular diameter (0.4 mm).
    tether_damping_N_s_m: float = 2.0
    payout_friction_N: float = 0.0005
    payout_viscosity_N_s_m: float = 0.0005

    duration_s: float = 3000.0
    sample_interval_s: float = 0.05
    max_step_s: float = 0.25
    rtol: float = 1e-8
    atol: float = 1e-10

    def __post_init__(self):
        for name in ("tether_youngs_modulus_Pa", "tether_diameter_m",
                     "initial_free_length_m", "total_tether_length_m"):
            if not np.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.initial_free_length_m > self.total_tether_length_m:
            raise ValueError("Initial free length exceeds total tether length")

    @property
    def tether_area_m2(self):
        return np.pi * self.tether_diameter_m**2 / 4

    @property
    def tether_axial_rigidity_N(self):
        return self.tether_youngs_modulus_Pa * self.tether_area_m2

    def tether_stiffness_N_m(self, free_length_m):
        """Axial stiffness EA/L for the current unstretched length outside the reel."""
        return self.tether_axial_rigidity_N / free_length_m

    @property
    def total_mass_kg(self):
        return self.mass_1_kg + self.mass_2_kg

    @property
    def reduced_mass_kg(self):
        return self.mass_1_kg * self.mass_2_kg / self.total_mass_kg

    @property
    def spring_energy_J(self):
        return 0.5 * self.spring_stiffness_N_m * self.spring_stroke_m**2


params = Parameters()


# %% State and internal forces
R = slice(0, 3)
V = slice(3, 6)
REL = slice(6, 9)
VEL = slice(9, 12)
LENGTH = 12
LOSS = 13


def initial_state(p: Parameters):
    y = np.zeros(14)
    radius = p.earth_radius_m + p.altitude_m
    y[R] = (radius, 0.0, 0.0)
    orbit_rate = np.sqrt(p.earth_mu_m3_s2 / radius**3) if p.gravity_enabled else 0.0
    y[V] = (0.0, orbit_rate * radius, 0.0)
    direction = np.asarray(p.initial_direction_rtn, dtype=float)
    direction = direction / np.linalg.norm(direction)
    y[REL] = p.initial_separation_m * direction
    angular_velocity = np.array([0.0, 0.0, orbit_rate + p.initial_pair_spin_rad_s])
    y[VEL] = (p.initial_separation_speed_m_s * direction
              + np.cross(angular_velocity, y[REL]))
    y[LENGTH] = p.initial_free_length_m
    return y


def positions(y, p: Parameters):
    """Recover both inertial positions from a state or a history (14, n)."""
    r1 = y[R] - p.mass_2_kg / p.total_mass_kg * y[REL]
    r2 = y[R] + p.mass_1_kg / p.total_mass_kg * y[REL]
    return r1, r2


def internal_forces(y, p: Parameters, spring_attached: bool, payout_available: bool):
    """Return spring [N], tether tension [N], payout speed [m/s], loss rate [W]."""
    distance = np.linalg.norm(y[REL])
    direction = y[REL] / max(distance, 1e-12)
    speed = float(np.dot(y[VEL], direction))
    compression = max(p.spring_stroke_m - (distance - p.initial_separation_m), 0.0)
    spring = p.spring_stiffness_N_m * compression if spring_attached else 0.0
    extension = distance - y[LENGTH]
    if extension <= 0.0:
        return spring, 0.0, 0.0, 0.0

    stiffness = p.tether_stiffness_N_m(y[LENGTH])
    elastic = stiffness * extension
    trial = elastic + p.tether_damping_N_s_m * speed
    payout_speed = 0.0
    if payout_available:
        payout_speed = max(
            0.0,
            (trial - p.payout_friction_N)
            / (p.tether_damping_N_s_m + p.payout_viscosity_N_s_m),
        )
    extension_rate = speed - payout_speed
    tension = max(0.0, elastic + p.tether_damping_N_s_m * extension_rate)
    # Account for force clipping and the change in U = 0.5 * (EA/L) * extension**2.
    # This ideal payout model treats released stiffness energy as an extra loss.
    stiffness_release = 0.5 * stiffness / y[LENGTH] * extension**2 * payout_speed
    loss_rate = (tension - elastic) * extension_rate + tension * payout_speed + stiffness_release
    return spring, tension, payout_speed, max(0.0, loss_rate)


def rhs(t, y, p: Parameters, spring_attached: bool, payout_available: bool):
    r1, r2 = positions(y, p)
    if p.gravity_enabled:
        g1 = -p.earth_mu_m3_s2 * r1 / np.linalg.norm(r1)**3
        g2 = -p.earth_mu_m3_s2 * r2 / np.linalg.norm(r2)**3
    else:
        g1 = g2 = np.zeros(3)
    spring, tension, payout_speed, loss_rate = internal_forces(
        y, p, spring_attached, payout_available,
    )
    direction = y[REL] / max(np.linalg.norm(y[REL]), 1e-12)
    dy = np.zeros_like(y)
    dy[R] = y[V]
    dy[V] = (p.mass_1_kg * g1 + p.mass_2_kg * g2) / p.total_mass_kg
    dy[REL] = y[VEL]
    dy[VEL] = g2 - g1 + (spring - tension) / p.reduced_mass_kg * direction
    dy[LENGTH] = payout_speed
    dy[LOSS] = loss_rate
    return dy


def rhs_jacobian(t, y, p: Parameters, spring_attached: bool, payout_available: bool):
    """Finite difference active state columns, with an exact zero loss column."""
    # The accumulated loss does not feed back into the equations. Supplying its
    # zero column avoids unbounded adaptive perturbations in long Radau runs.
    dynamics = partial(rhs, t, p=p, spring_attached=spring_attached,
                       payout_available=payout_available)
    step = np.sqrt(np.finfo(float).eps) * np.maximum(np.abs(y[:LOSS]), 1e-3)
    jacobian = np.zeros((y.size, y.size))
    jacobian[:, :LOSS] = approx_fprime(
        y[:LOSS], lambda active: dynamics(np.append(active, y[LOSS])), epsilon=step,
    )
    return jacobian


# %% Integrate, restarting at spring release and the reel end stop
@dataclass
class Simulation:
    params: Parameters
    time_s: np.ndarray
    state: np.ndarray
    events: dict[str, list[float]]


def simulate(p: Parameters = params):
    y = initial_state(p)
    initial_extension = max(p.initial_separation_m - p.initial_free_length_m, 0.0)
    relative_energy = (p.spring_energy_J
                       + 0.5 * p.reduced_mass_kg * np.dot(y[VEL], y[VEL])
                       + 0.5 * p.tether_stiffness_N_m(p.initial_free_length_m) * initial_extension**2)
    contact_speed_scale = np.sqrt(2 * relative_energy / p.reduced_mass_kg)
    if p.gravity_enabled:
        orbit_rate_squared = p.earth_mu_m3_s2 / np.linalg.norm(y[R])**3
        contact_speed_scale += (3 * orbit_rate_squared * p.duration_s
                                * max(p.initial_separation_m, p.total_tether_length_m))
    # Limit travel per step so a rapid approach does not skip the contact event.
    # The energy bound is exact without gravity. The tidal addition is an estimate.
    max_step = min(p.max_step_s, 0.5 * p.collision_distance_m / max(contact_speed_scale, 1e-12))
    spring_attached = p.spring_stiffness_N_m > 0 and p.spring_stroke_m > 0
    payout_available = p.initial_free_length_m < p.total_tether_length_m
    event_times = {name: [] for name in (
        "spring_release", "full_payout", "collision", "tether_taut", "tether_slack",
    )}
    segments = []
    start = 0.0

    def collision(t, state):
        return np.linalg.norm(state[REL]) - p.collision_distance_m

    def spring_release(t, state):
        return np.linalg.norm(state[REL]) - p.initial_separation_m - p.spring_stroke_m

    def full_payout(t, state):
        return state[LENGTH] - p.total_tether_length_m

    def tether_taut(t, state):
        return np.linalg.norm(state[REL]) - state[LENGTH]

    def tether_slack(t, state):
        return tether_taut(t, state)

    collision.terminal, collision.direction = True, -1
    spring_release.terminal, spring_release.direction = True, 1
    full_payout.terminal, full_payout.direction = True, 1
    tether_taut.direction, tether_slack.direction = 1, -1

    # There are at most two irreversible mode changes, followed by a final phase.
    for _ in range(3):
        events = [collision, tether_taut, tether_slack]
        if spring_attached:
            events.append(spring_release)
        if payout_available:
            events.append(full_payout)
        sol = solve_ivp(
            partial(rhs, p=p, spring_attached=spring_attached,
                    payout_available=payout_available),
            (start, p.duration_s), y, method="Radau", dense_output=True,
            events=events, rtol=p.rtol, atol=p.atol, max_step=max_step,
            jac=partial(rhs_jacobian, p=p, spring_attached=spring_attached,
                        payout_available=payout_available),
        )
        if not sol.success:
            raise RuntimeError(sol.message)
        segments.append(sol)
        for event, times in zip(events, sol.t_events):
            history = event_times[event.__name__]
            for time in times:
                if not history or abs(time - history[-1]) > 1e-8:
                    history.append(float(time))
        start = float(sol.t[-1])
        y = sol.y[:, -1].copy()
        if event_times["collision"] or sol.status == 0 or start >= p.duration_s:
            break
        if spring_attached and sol.t_events[events.index(spring_release)].size:
            spring_attached = False
        if payout_available and sol.t_events[events.index(full_payout)].size:
            y[LENGTH] = p.total_tether_length_m
            payout_available = False

    # Include accepted solver points to help resolve short force peaks.
    regular_times = np.arange(0.0, start, p.sample_interval_s)
    times = np.unique(np.concatenate([regular_times, [start], *[s.t for s in segments]]))
    states = np.empty((14, times.size))
    for sol in segments:
        mask = (times >= sol.t[0]) & (times <= sol.t[-1])
        states[:, mask] = sol.sol(times[mask])
    return Simulation(p, times, states, event_times)


# %% Diagnostics: forces, motion, and an energy balance

def diagnostics(run: Simulation):
    p, times, y = run.params, run.time_s, run.state
    distance = np.linalg.norm(y[REL], axis=0)
    speed = np.sum(y[REL] * y[VEL], axis=0) / distance
    release = run.events["spring_release"]
    stop = run.events["full_payout"]
    forces = np.array([
        internal_forces(
            state, p,
            p.spring_stiffness_N_m > 0 and p.spring_stroke_m > 0
            and (not release or time < release[0]),
            p.initial_free_length_m < p.total_tether_length_m
            and (not stop or time < stop[0]),
        )
        for time, state in zip(times, y.T)
    ])
    spring, tension, payout_speed, _ = forces.T
    stiffness = p.tether_stiffness_N_m(y[LENGTH])
    extension = np.maximum(distance - y[LENGTH], 0.0)
    compression = np.maximum(p.spring_stroke_m - (distance - p.initial_separation_m), 0.0)
    if p.spring_energy_J == 0:
        compression[:] = 0.0
    elif release:
        compression[times >= release[0]] = 0.0
    energy = (0.5 * p.total_mass_kg * np.sum(y[V]**2, axis=0)
              + 0.5 * p.reduced_mass_kg * np.sum(y[VEL]**2, axis=0)
              + 0.5 * p.spring_stiffness_N_m * compression**2
              + 0.5 * stiffness * extension**2)
    gravity_gradient_force = np.zeros_like(distance)
    if p.gravity_enabled:
        r1, r2 = positions(y, p)
        radius_1 = np.linalg.norm(r1, axis=0)
        radius_2 = np.linalg.norm(r2, axis=0)
        g1 = -p.earth_mu_m3_s2 * r1 / radius_1**3
        g2 = -p.earth_mu_m3_s2 * r2 / radius_2**3
        gravity_gradient_force = p.reduced_mass_kg * np.linalg.norm(g2 - g1, axis=0)
        energy -= p.earth_mu_m3_s2 * (
            p.mass_1_kg / radius_1 + p.mass_2_kg / radius_2
        )
    return {
        "separation_m": distance,
        "separation_speed_m_s": speed,
        "extension_m": extension,
        "tether_stiffness_N_m": stiffness,
        "spring_force_N": spring,
        "tension_N": tension,
        "gravity_gradient_force_N": gravity_gradient_force,
        "payout_speed_m_s": payout_speed,
        "mechanical_energy_J": energy,
        "energy_residual_J": energy - energy[0] + y[LOSS],
    }


def summary(run: Simulation, data=None):
    p = run.params
    data = diagnostics(run) if data is None else data
    ideal_speed = np.sqrt(2 * p.spring_energy_J / p.reduced_mass_kg)
    print(f"Young's modulus: {p.tether_youngs_modulus_Pa / 1e9:g} GPa")
    print(f"Tether diameter: {p.tether_diameter_m * 1000:g} mm")
    print(f"Stiffness at full payout: {p.tether_stiffness_N_m(p.total_tether_length_m):.4g} N/m")
    print(f"Spring energy: {p.spring_energy_J:.4g} J")
    print(f"Ideal relative speed from rest, with spring alone: {ideal_speed:.4g} m/s")
    for name in ("spring_release", "full_payout", "collision"):
        times = run.events[name]
        label = name.replace("_", " ").capitalize()
        if times:
            value = f"{times[0]:.4f} s"
        elif name == "full_payout" and p.initial_free_length_m == p.total_tether_length_m:
            value = "already fully paid out at t = 0"
        elif name == "spring_release" and p.spring_energy_J == 0:
            value = "spring disabled"
        else:
            value = "not reached during this run"
        print(f"{label}: {value}")
    print(f"Maximum separation: {data['separation_m'].max():.4f} m")
    print(f"Final free tether length: {run.state[LENGTH, -1]:.4f} m")
    print(f"Peak tether tension (sampled): {data['tension_N'].max():.4g} N")
    print(f"Peak gravity gradient force (sampled): {data['gravity_gradient_force_N'].max():.4g} N")
    print(f"Dissipated energy: {run.state[LOSS, -1]:.4g} J")
    print(f"Maximum absolute energy residual: {np.max(np.abs(data['energy_residual_J'])):.3g} J")
    if run.events["collision"]:
        print("STOPPED at the contact distance. Contact dynamics are outside this model.")


# %% Run the material and length combinations

def compare_materials(p: Parameters = params):
    """Hold other inputs fixed and vary effective Young's modulus and total length."""
    return {
        (material, length): simulate(replace(
            p, tether_youngs_modulus_Pa=modulus, total_tether_length_m=length,
        ))
        for material, modulus in MATERIAL_YOUNGS_MODULUS_PA.items()
        for length in TETHER_LENGTHS_M
    }


# %% Separate comparison grids for each tether length

def plot_comparison(runs, separation_view="rtn"):
    """Plot one tether length, with one material per row and three quantities."""
    if not runs or separation_view not in ("rtn", "time"):
        raise ValueError("Provide runs and choose separation_view='rtn' or 'time'")
    lengths = {length for _, length in runs}
    if len(lengths) != 1:
        raise ValueError("Use plot_comparisons_by_length for multiple tether lengths")
    length = next(iter(lengths))
    materials = list(dict.fromkeys(material for material, _ in runs))
    end_time = max(run.time_s[-1] for run in runs.values())
    fig, axes = plt.subplots(
        len(materials), 3, figsize=(15, 3.6 * len(materials)), squeeze=False,
        sharex="col", sharey="col", layout="constrained",
    )
    for row, material in enumerate(materials):
        force_ax, separation_ax, speed_ax = axes[row]
        run = runs[material, length]
        t, y, p = run.time_s, run.state, run.params
        data = diagnostics(run)
        force_ax.plot(t, data["tension_N"], color="tab:blue", label="Tether tension")
        force_ax.plot(t, data["gravity_gradient_force_N"], "--", color="tab:green",
                      label="Gravity gradient magnitude")
        force_ax.plot(t, data["spring_force_N"], ":", color="tab:orange",
                      label="Separating spring")
        speed_ax.plot(t, data["separation_speed_m_s"], color="tab:blue")
        if separation_view == "time":
            separation_ax.plot(t, data["separation_m"], color="tab:blue")
            separation_ax.set(ylabel="Centre separation [m]", xlim=(0, end_time))
        else:
            radial = y[R] / np.linalg.norm(y[R], axis=0)
            if p.gravity_enabled:
                normal = np.cross(y[R].T, y[V].T).T
                normal /= np.linalg.norm(normal, axis=0)
            else:
                normal = np.broadcast_to(np.array([[0.0], [0.0], [1.0]]), radial.shape)
            along_track = np.cross(normal.T, radial.T).T
            relative_radial = np.sum(y[REL] * radial, axis=0)
            relative_along_track = np.sum(y[REL] * along_track, axis=0)
            separation_ax.plot(relative_along_track, relative_radial, color="tab:blue")
            separation_ax.scatter(relative_along_track[-1], relative_radial[-1],
                                  color="tab:blue", marker="x", s=30)
            separation_ax.set_ylabel("Radial outward [m]")
        force_ax.set_ylabel(f"{material}\nForce [N]")
        force_ax.set_yscale("symlog", linthresh=1e-8)
        speed_ax.set_ylabel("Separation speed [m/s]")
        speed_ax.axhline(0, color="0.5", lw=0.7)
        # Linear time axes use this length's actual run window, shared across rows.
        for ax in (force_ax, speed_ax):
            ax.set_xlim(0, end_time)
        for ax in axes[row]:
            ax.grid(alpha=0.25)
    axes[0, 0].set_title("Force magnitudes")
    axes[0, 1].set_title("Separation over time" if separation_view == "time"
                         else "RTN separation (cross = end)")
    axes[0, 2].set_title("Separation speed (negative = rebound)")
    axes[-1, 0].set_xlabel("Time [s]")
    axes[-1, 1].set_xlabel("Time [s]" if separation_view == "time" else "Along track [m]")
    axes[-1, 2].set_xlabel("Time [s]")
    handles, _ = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles=handles, loc="outside lower center", ncols=3, fontsize=9)
    diameter_mm = next(iter(runs.values())).params.tether_diameter_m * 1000
    fig.suptitle(f"{length:g} m tether: {diameter_mm:g} mm diameter, assumed effective moduli")
    return fig


def plot_comparisons_by_length(runs, separation_view="rtn"):
    """Return one independent figure per tether length."""
    if not runs:
        raise ValueError("Provide runs")
    return {
        length: plot_comparison(
            {case: run for case, run in runs.items() if case[1] == length},
            separation_view=separation_view,
        )
        for length in sorted({length for _, length in runs})
    }


# %% Display separate 2x3 grids for 2 m and 200 m, with one material per row
# Use "time" for centre separation versus time, or "rtn" for the existing trajectory.
SEPARATION_VIEW = "rtn"
if __name__ == "__main__":
    comparisons = compare_materials(params)
    for (material, length), run in comparisons.items():
        print(f"\n{material}, {length:g} m")
        summary(run)
    figures = plot_comparisons_by_length(comparisons, separation_view=SEPARATION_VIEW)
    plt.show()
