"""Constant-condition energy and independent coulomb balances for one interval.

Chain instances to represent chronological sunlight, eclipse, survival and recovery.
Power is at the source and load boundaries. Battery voltage is supplied, not fitted.
"""
import json
import math
import sys


def analyze(p):
    for name, value in p.items():
        if name in ('charge_allowed', 'shunt_surplus'):
            if type(value) is not bool:
                raise ValueError(name + ' must be Boolean.')
        elif isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError(name + ' must be finite.')
    for name in ('duration_s', 'battery_voltage_V', 'energy_capacity_J', 'charge_capacity_C'):
        if p[name] <= 0:
            raise ValueError(name + ' must be positive.')
    for name in ('source_efficiency', 'load_efficiency', 'charge_efficiency', 'discharge_efficiency',
                 'coulomb_charge_efficiency', 'coulomb_discharge_efficiency'):
        if not 0 < p[name] <= 1:
            raise ValueError(name + ' must lie in (0, 1].')
    for name in ('source_power_W', 'load_power_W', 'charge_current_limit_A', 'discharge_current_limit_A', 'surplus_capacity_W'):
        if p[name] < 0:
            raise ValueError(name + ' must be nonnegative.')
    if not 0 <= p['soc_min'] <= 1 or not 0 <= p['soc_initial'] <= 1:
        raise ValueError('Initial SOC and minimum SOC must lie in [0, 1].')
    if not 0 <= p['energy_reserve_J'] <= p['energy_capacity_J'] or not 0 <= p['energy_initial_J'] <= p['energy_capacity_J']:
        raise ValueError('Initial energy and reserve must fit the retained capacity.')
    for prefix in ('charge', 'discharge'):
        if not -273.15 < p[prefix + '_temp_min_C'] <= p[prefix + '_temp_max_C']:
            raise ValueError(prefix + ' temperature interval is invalid.')
    if p['temperature_C'] <= -273.15:
        raise ValueError('Temperature must exceed absolute zero.')

    duration, voltage = p['duration_s'], p['battery_voltage_V']
    energy, charge = p['energy_initial_J'], p['soc_initial'] * p['charge_capacity_C']
    source = p['source_power_W'] * p['source_efficiency']
    demand = p['load_power_W'] / p['load_efficiency']
    delta = source - demand
    accepted = discharged = stored = removed = unserved = surplus = 0.0
    active = duration
    peak_charge = peak_discharge = 0.0
    charge_temp_ok = discharge_temp_ok = True
    if delta >= 0:
        headroom = energy < p['energy_capacity_J'] and charge < p['charge_capacity_C']
        charge_temp_ok = not (delta > 0 and headroom and p['charge_allowed']) or (
            p['charge_temp_min_C'] <= p['temperature_C'] <= p['charge_temp_max_C'])
        power = min(delta, p['charge_current_limit_A'] * voltage) if p['charge_allowed'] and charge_temp_ok else 0.0
        if power > 0:
            current = power / voltage
            active = min(duration, (p['energy_capacity_J'] - energy) / (power * p['charge_efficiency']),
                         (p['charge_capacity_C'] - charge) / (current * p['coulomb_charge_efficiency']))
            peak_charge = current if active > 0 else 0.0
            accepted = power * active
            stored = accepted * p['charge_efficiency']
            energy += stored
            charge += current * p['coulomb_charge_efficiency'] * active
        surplus = delta * duration - accepted
        peak_surplus = delta if active < duration or power == 0 else delta - power
        service_duration = duration
    else:
        deficit = -delta
        discharge_temp_ok = p['discharge_temp_min_C'] <= p['temperature_C'] <= p['discharge_temp_max_C']
        power = min(deficit, p['discharge_current_limit_A'] * voltage)
        if power > 0:
            current = power / voltage
            active = min(duration, energy * p['discharge_efficiency'] / power,
                         charge * p['coulomb_discharge_efficiency'] / current)
            peak_discharge = current if active > 0 else 0.0
            discharged = power * active
            removed = discharged / p['discharge_efficiency']
            energy -= removed
            charge -= current / p['coulomb_discharge_efficiency'] * active
        else:
            active = 0.0
        unserved = max(0.0, (deficit * duration - discharged) * p['load_efficiency'])
        peak_surplus = 0.0
        service_duration = active if power >= deficit else 0.0
    energy = min(p['energy_capacity_J'], max(0.0, energy))
    soc = min(1.0, max(0.0, charge / p['charge_capacity_C']))
    minimum_energy, minimum_soc = min(energy, p['energy_initial_J']), min(soc, p['soc_initial'])
    shunted = surplus if p['shunt_surplus'] else 0.0
    losses = ((p['source_power_W'] - source) * duration
              + (demand * duration - unserved / p['load_efficiency']) * (1 - p['load_efficiency'])
              + accepted - stored + removed - discharged + shunted)
    return dict(energy_end_J=energy, soc_end=soc, energy_min_J=minimum_energy, soc_minimum=minimum_soc,
                source_energy_J=p['source_power_W'] * duration, load_energy_J=p['load_power_W'] * duration,
                served_energy_J=p['load_power_W'] * duration - unserved, unserved_energy_J=unserved,
                service_duration_s=service_duration, accepted_charge_energy_J=accepted,
                discharge_energy_J=discharged, stored_energy_J=stored, removed_energy_J=removed,
                surplus_energy_J=surplus, peak_surplus_W=peak_surplus, loss_energy_J=losses,
                shunt_energy_J=shunted, curtailed_energy_J=surplus - shunted,
                peak_charge_current_A=peak_charge, peak_discharge_current_A=peak_discharge,
                energy_reserve_ok=minimum_energy >= p['energy_reserve_J'], soc_reserve_ok=minimum_soc >= p['soc_min'],
                charge_temperature_ok=charge_temp_ok, discharge_temperature_ok=discharge_temp_ok,
                surplus_supported=peak_surplus <= p['surplus_capacity_W'])


if __name__ == '__main__':
    try:
        json.dump(analyze(json.load(sys.stdin)['inputs']), sys.stdout, allow_nan=False)
    except (ValueError, KeyError, TypeError, ArithmeticError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
