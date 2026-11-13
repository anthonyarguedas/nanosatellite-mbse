"""Independent references. No framework imports, calls or source introspection.

Decimal is used for scalar accounting. Orbit integration uses equal time
(mean anomaly) midpoints, a Newton Kepler solve, Cartesian cylindrical shadow
and explicit inertial panel normals. It does not find analytic shadow roots.
"""
from decimal import Decimal, localcontext, ROUND_CEILING
import math
from functools import lru_cache
import numpy as np


def D(x):
    return Decimal(str(x))


def product(*xs):
    with localcontext() as c:
        c.prec = 40
        y = D(1)
        for x in xs:
            y *= D(x)
        return float(y)


def quotient(a, b):
    with localcontext() as c:
        c.prec = 40
        return float(D(a) / D(b))


def total(xs):
    return float(sum((D(x) for x in xs), D(0)))


def count(power, per_cell, series=1):
    with localcontext() as c:
        c.prec = 40
        x = D(power) / D(per_cell) / D(series)
        return float(x), int(x.to_integral_value(rounding=ROUND_CEILING))


def sampled(points):
    products = [product(v, i) for v, i in points]
    index = products.index(max(products))
    return dict(voltage=points[index][0], current=points[index][1], power=products[index],
                voc=points[-1][0], isc=points[0][1], products=products)


def imposed(points, ns, np_, voltage):
    # Independent Decimal straight-line evaluation, without framework validation.
    v = D(voltage) / D(ns)
    for vx, ix in points:
        if v == D(vx):
            i = D(ix) * D(np_)
            return float(i), float(D(voltage) * i)
    for (v0, i0), (v1, i1) in zip(points, points[1:]):
        if D(v0) < v < D(v1):
            i = (D(i0) + (v-D(v0)) * (D(i1)-D(i0)) / (D(v1)-D(v0))) * D(np_)
            return float(i), float(D(voltage) * i)
    raise ValueError('Independent reference: voltage outside characteristic')


def period(a, mu):
    return 2 * math.pi * math.sqrt(a ** 3 / mu)


@lru_cache(maxsize=64)
def orbit(a, e, radius, mu, beta_deg, lambda_deg, pointing, samples=262144):
    """Sun-facing +Z, or +Z radial outward while -Z points to nadir.

    These explicit restricted attitudes avoid reproducing the model's general
    face/clocking matrix. Cartesian radial outward is position / radius.
    """
    T = period(a, mu)
    M = 2 * math.pi * (np.arange(samples, dtype=float) + .5) / samples
    E = M.copy()
    for _ in range(10):
        E -= (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    residual = float(np.max(np.abs(E - e*np.sin(E) - M)))
    x, y = a*(np.cos(E)-e), a*math.sqrt(1-e*e)*np.sin(E)
    b, l = math.radians(beta_deg), math.radians(lambda_deg)
    sun = np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])
    dot = x*sun[0] + y*sun[1]
    rr = x*x + y*y
    lit = ~((dot < 0) & ((rr-dot*dot) < radius*radius))
    nlit = int(lit.sum())
    Ts = T * nlit / samples
    if pointing == 'sun_pointing':
        projection = 1.0
    elif pointing == 'nadir':
        projection = float(np.maximum(0, dot/np.sqrt(rr))[lit].mean())
    else:
        raise ValueError('Reference supports only explicitly selected attitudes')
    return dict(period=T, sunlight=Ts, eclipse=T-Ts, projection=projection,
                projected_duration=Ts*projection, kepler_residual_rad=residual,
                sample_count=samples, duration_grid_bound_s=2*T/samples)


def sizing(c, orb):
    """Independent algebra from case declarations, never from actual results."""
    a, b, l = c['array'], c['battery'], c['loads']
    ns, np_ = a['series'], a['parallel']
    powers = [product(x['voltage'], x['current']) for x in l['states']]
    ps = total([product(p, x['sun_duty']) for p, x in zip(powers,l['states'])])
    pe = total([product(p, x['eclipse_duty']) for p, x in zip(powers,l['states'])])
    es, ee = product(ps,orb['sunlight']), product(pe,orb['eclipse'])
    required = quotient(total([quotient(es,c['sun_path']), quotient(ee,c['eclipse_path'])]),orb['sunlight'])
    v, i, voc, isc = a['vmp'], a['imp'], a['voc'], a['isc']
    cp = product(v, i)
    fractional, integer = count(required, cp)
    minpar = count(required, cp, ns)[1]
    cycles = quotient(product(c['lifetime'],c['days_per_year'],86400),orb['period'])
    dod = max(b['fit_min'], min(b['fit_max'], (cycles/b['fit_a'])**(1/b['fit_b'])))
    energy = product(quotient(ee,dod),1+b['margin'])
    active = product(ns,np_,a['area'])
    eff = quotient(cp,product(a['area'],a['reference_irradiance']))
    density = product(c['irradiance'],eff,c['inherent'],c['assembly'],orb['projection'])
    available = product(active,density)
    packwh = product(b['series'],b['parallel'],b['cell_wh'])
    packah = product(b['parallel'],b['cell_ah'])
    return dict(state_powers=powers, sun_power=ps, eclipse_power=pe,
                sunlight_energy=es,eclipse_energy=ee,required_power=required,
                cell_power=cp,fractional_count=fractional,required_count=integer,
                minimum_solar_parallel=minpar, cycles=cycles,dod=dod,
                required_battery_energy=energy,
                minimum_battery_parallel=count(energy,product(b['cell_wh'],3600),b['series'])[1],
                active_area=active,panel_area=quotient(active,a['packing']),
                required_area=quotient(required,density),
                effective_area=quotient(required,product(c['irradiance'],eff)),
                tumbling_area=quotient(2*quotient(required,product(c['irradiance'],eff)),math.cos(math.radians(50))*a['packing']),
                generation_efficiency=eff,density=density,available_power=available,
                source_energy=product(available,orb['sunlight']),
                array_voltage=product(ns,v),array_current=product(np_,i),
                array_voc=product(ns,voc),array_isc=product(np_,isc),array_mpp=product(ns,np_,cp),
                pack_wh=packwh,pack_ah=packah,pack_j=product(packwh,3600),
                eol_j=product(packwh,3600,b['energy_retention']),
                eol_ah=product(packah,b['capacity_retention']),
                battery_voltage=product(b['series'],b['nominal']),
                battery_min=product(b['series'],b['minimum']),battery_max=product(b['series'],b['maximum']),
                charge_limit=product(b['parallel'],b['charge_limit']),
                discharge_limit=product(b['parallel'],b['discharge_limit']))


def corners(powers, lo, hi):
    return quotient(min(powers), hi), quotient(max(powers), lo)


def rectangular_layout(d):
    """Maximum rectangular extent from independent Decimal arithmetic."""
    width = total([product(d['columns'],total([d['package_width_m'],d['package_dimension_tolerance_m']])),
                   product(d['columns']-1,d['gap_m']),product(2,d['edge_clearance_m'])])
    length = total([product(d['rows'],total([d['package_length_m'],d['package_dimension_tolerance_m']])),
                    product(d['rows']-1,d['gap_m']),product(2,d['edge_clearance_m'])])
    return dict(width=width,length=length,footprint=product(width,length),
                plate_area=product(d['plate_width_m'],d['plate_length_m']))
