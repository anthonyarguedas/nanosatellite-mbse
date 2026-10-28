# CubeSat deployment and orbital lifetime

Two identical 1.5U CubeSats start coupled in a 600 km Sun synchronous orbit. The spring releases at time zero. Both spacecraft continue through tether extension, recoil, collisions and the first three days in one continuous Basilisk integration. Medium activity atmospheric drag acts on both live bodies throughout.

The detailed deployment mode has one physical trajectory and one Vizard recording. The orbit view and the close-up use the same states and timestamps. No separate pre-release orbit is substituted. A separate fast lifetime mode estimates atmospheric drag over several years.

## Open the result

From `cubics-proposal`:

```bash
.venv/bin/python tether-simulation/view_vizard.py
```

The launcher prints the file it opens. The previous `--scene orbit` and `--scene deployment` options remain accepted. They now open the same continuous recording.

In Vizard:

- The main Earth view shows the real orbital track.
- GUI zoom follows the same two bodies on the same timeline.
- For clear meter scale detail, use `Cameras > Change Main Camera Target > Deployment_center`. This puts Vizard in the spacecraft local view.
- Select `earth` as the camera target to return to the global orbit view. The physical CubeSats are too small to resolve at Earth scale.
- Playback starts in real time. Use the `+` control to accelerate the remainder of the orbit. Press `h` for other controls.

The default events are approximately:

| Event | Simulation time |
| --- | --- |
| Spring release | 0 s |
| First taut tether | 30.12 s |
| First bus collision | 60.9 s |
| End of the default continuous run | 259200 s, or 72 hours (about 44.68 design orbits) |

Later contacts and motion follow the dynamics. The simulation does not relatch the pair, repeat the spring push, avoid collisions or restart the orbit.

## Run again

```bash
.venv/bin/python tether-simulation/simulate.py --open
```

The default integrates 72 hours from release at a fixed 5 ms step. Both spacecraft, gravity, drag, attachment torques and collision detection remain active throughout. This is about 51.84 million integration intervals. Computation and recording can take around an hour or more on this machine.

Long runs stream directly to disk. Progress is printed to the terminal and saved to `output/run_status.json`, including simulated time, contact count and a running time estimate. The same two spacecraft continue through every integration interval. Output sampling changes without restarting the dynamics.

While a run is active, new files have a `.part` suffix. The previous complete recording remains untouched. The new `mission.bin`, `mission.csv`, event log and summary replace the complete outputs only after the requested duration has finished. The launcher reports an unfinished run instead of silently opening an older recording.

```bash
# A shorter continuous test, including the first impacts.
.venv/bin/python tether-simulation/simulate.py \
  --duration 180 --output /tmp/tether-test --open

# Explicitly request the first three days.
.venv/bin/python tether-simulation/simulate.py --days 3 --open

# A shorter continuous run, or a finer integration step.
.venv/bin/python tether-simulation/simulate.py --orbits 1 --open
.venv/bin/python tether-simulation/simulate.py --duration 180 --step 0.0025

# Disable drag for a gravity and tether regression check.
.venv/bin/python tether-simulation/simulate.py --duration 180 --no-drag

# Change the illustrative collision restitution.
.venv/bin/python tether-simulation/simulate.py --restitution 1
```

Install Python dependencies with:

```bash
python -m pip install -r tether-simulation/requirements.txt
```

Vizard is the supported 3D viewer. The retired HTML/GIF viewer is no longer included. Static lifetime plots remain available.

Vizard is a separate application. The local official macOS Vizard 2.4 build is in `.tools/Vizard.app`, excluded from Git. On another machine, [download Vizard](https://avslab.github.io/basilisk/Vizard/VizardDownload.html) and pass `view_vizard.py --app /path/to/Vizard.app`.

## Outputs

- `output/mission.bin`: the complete continuous Vizard recording, including both views.
- `output/mission.csv`: actual spacecraft positions, velocities, attitudes, angular velocities, attachment positions and tether tension.
- `output/results.json`: inputs, completed duration, altitude range, drag work and contact statistics.
- `output/collision_events.jsonl`: every completed collision episode from a streaming run.
- `output/run_status.json`: current progress or completion status.

Old separate orbit and short deployment recordings are obsolete.

The streaming run records every 20 ms during the first 120 s, every 50 ms around later tether snatches and impacts, and every 200 ms in quiet intervals. The start of each contact episode is recorded at its actual integration timestamp. CSV and Vizard packets use the same live states and timestamps. Both spacecraft continue to integrate at 5 ms regardless of recording cadence.

Only a small set of current states is retained in memory. Closed contact episodes are written to the event log and released from memory. Native display geometry calculations are compiled. These changes affect recording cost rather than the spacecraft dynamics.

The default output limit is 28 GiB and the free disk reserve is 5 GiB. These limits can be adjusted with `--max-output-gib` and `--reserve-free-gib`. A storage limit or interruption preserves the partial files and writes `partial_results.json`. It is never reported as a completed three day run.

## Eight year drag screening

Run three mission years and five additional years from `cubics-proposal`:

```bash
.venv/bin/python tether-simulation/lifetime.py

# Open the completed coupled orbit and tether simulation separately.
.venv/bin/python tether-simulation/view_vizard.py

# Assume ideal orbit maintenance during the mission, then passive decay.
.venv/bin/python tether-simulation/lifetime.py \
  --maintain-mission-altitude --output /tmp/maintained-lifetime

# Set the mean projected area of the whole pair in each phase.
.venv/bin/python tether-simulation/lifetime.py \
  --mission-years 3 --post-mission-years 5 \
  --mission-area-m2 0.03 --post-mission-area-m2 0.0452
```

The default run takes a few seconds. It averages atmospheric drag over each orbit and integrates mean circular altitude with an adaptive solver. This avoids the roughly 50 billion 5 ms integration steps required to extend the detailed deployment to eight years. The detailed deployment and its existing outputs remain unchanged.

The default lifetime assumptions are:

- Initial mean circular altitude of 600 km, with the original SSO design inclination.
- Total pair mass of 6 kg and an assumed drag coefficient of 2.2.
- Mean projected area of about 0.04522 m² for the pair in both phases. This uses isotropic mean cuboid projections and the physical 0.5 mm tether. Mutual shadowing is omitted.
- Passive decay throughout all eight years. The end of the mission is a reporting milestone. Use `--maintain-mission-altitude` to assume ideal stationkeeping during the first three years. That option does not calculate fuel use.
- The buses remain connected and intact. Relative tether motion, collisions and attitude evolution are omitted.

Atmospheric density comes from Basilisk's native [NRLMSISE-00 module](https://avslab.github.io/basilisk/Documentation/simulation/environment/MsisAtmosphere/msisAtmosphere.html). Density and drag work are averaged over 24 orbital phases, four node longitudes and four seasons. Atmospheric co-rotation is included. Local solar time is unspecified and is averaged over. A 10 km altitude grid uses logarithmic interpolation. Propagation stops at a mean altitude of 120 km. Atmospheric entry and burnup are outside this model.

Only medium solar activity is used, with F10.7 fixed at 140 sfu and Ap at 10. This is a screening assumption, not a forecast. The default results are approximately:

| Milestone | Elapsed time | Mean altitude |
| --- | --- | --- |
| Initial orbit | 0 years | 600.0 km |
| Mission end | 3 years | 584.9 km |
| Five years after mission end | 8 years | 549.3 km |

The additional decay during the five years after mission end is about 35.6 km.

These results depend strongly on solar activity and projected area. A mission prediction needs a solar activity history or forecast ensemble and a justified attitude and area model. This screening analysis does not establish disposal compliance.

Lifetime outputs are separate from the deployment files:

- `output/lifetime.png` and `output/lifetime.svg`: altitude over the full eight years, with mission end marked at year three.
- `output/lifetime.csv`: daily mean altitude samples and exact mission milestones for medium solar activity. Propagation stops if the 120 km boundary is reached.
- `output/lifetime_atmosphere.csv`: the averaged atmosphere and drag work tables used in the run.
- `output/lifetime_results.json`: assumptions, inputs, milestone altitudes, decay during each phase and boundary crossing times.
The reduced lifetime model produces numerical results only. Its former fixed-tether milestone visualization is obsolete. All launcher scene aliases now open the continuous `mission.bin`, which contains the actual orbital, spring, tether, attitude and contact states. GUI zoom operates on those same bodies.

The lifetime altitude is a mean circular altitude above the equatorial reference radius. The detailed deployment instead starts at an osculating altitude of 600 km and includes periodic J2 motion. The lifetime mode uses J2 only to select the initial SSO inclination. It omits plane evolution, short period J2 altitude variation, solar radiation pressure and third body effects.

## Orbit

| Parameter | Default |
| --- | --- |
| Initial osculating altitude | 600 km above the 6378.137 km equatorial reference radius |
| Initial eccentricity | 0 |
| Initial inclination | About 97.7877 degrees, retrograde |
| RAAN | 0 degrees |
| Initial argument of latitude | 0 degrees, ascending node |
| Epoch | 2026-01-01 00:00:00 UTC |
| Two body design period | 5801.23 s, or 96.687 min |
| Initial common orbital speed | About 7.558 km/s |
| Gravity | Earth point mass plus J2, normalized C20 only |

The inclination solves the first order secular J2 condition:

```text
n = sqrt(mu / a^3)
dOmega/dt = -(3/2) J2 n (Re/a)^2 cos(i) = 2 pi / tropical_year
```

The target nodal drift is about +0.98565 degrees per day. This is a first order SSO design. Mean and osculating elements differ. Precise long term local solar time control would require refinement and stationkeeping.

The 600 km value specifies the initial osculating altitude. J2 produces periodic altitude variation. The actual COM altitude range is written to `results.json`. This altitude uses the equatorial reference radius rather than geodetic height above the oblate surface.

RAAN is a free initial phase. No local time of ascending node is specified. Vizard uses the epoch for Earth rotation and a low precision geocentric Sun position for lighting. Solar gravity and radiation pressure are omitted.

## Spacecraft, spring and tether

| Item | Default |
| --- | --- |
| Mass | 3 kg per identical 1.5U bus |
| Bus envelope | 170.2 × 100 × 100 mm, uniform cuboid |
| Initial configuration | Facing ends touch, stationary in the local orbit frame |
| Initial orientation | Long axis along track, third body axis radial |
| Initial angular velocity | Local orbital angular rate |
| Attachment points | Centers of the two facing ends |
| Nylon tether | 3 m unstretched length, 0.5 mm diameter |
| Assumed effective nylon modulus | 2 GPa |
| Axial tether stiffness | About 130.9 N/m |
| Tether mechanics | Massless, linear elastic, tension only |
| Spring | 20 mm stroke, 37.5 N/m, 7.5 mJ initial stored energy |
| Release speed | 0.10 m/s relative between bus centers, about 0.05 m/s each about their COM |

Mass follows the typical 1.5U maximum in [CubeSat Design Specification Rev. 14.1, Table 1](https://www.cubesat.org/s/CDS-REV14_1-2022-02-09.pdf). Launch provider limits take precedence. Nylon diameter and modulus are illustrative assumptions.

The tether force is zero while slack and tensile when stretched. Elastic stretch allows the loaded attachment distance to slightly exceed 3 m. The tether then recoils. Intrinsic nylon damping is omitted. Its force acts at the actual rotating attachment points and includes their lever arm torques.

The release speed is an initial deployment condition. Later contact point and attachment velocities can differ as the buses rotate and collide.

## Collision model

Collisions are allowed and resolved during the same simulation. There is no collision avoidance or relatching.

Contact detection uses oriented cuboids and the 15 separating axes. A single representative contact point gives a frictionless normal impulse. The default normal coefficient of restitution is **0.3**, an explicit assumption. Use zero for a perfectly inelastic normal response or one for an elastic normal response. Tangential motion and spin are free.

The impulse changes the live Basilisk hub velocities and angular velocities. Equal and opposite impulses preserve the pair's linear momentum. Contact impulses preserve angular momentum about the contact point. A small mass balanced position correction removes numerical penetration after a discrete integration step. The maximum penetration before correction is reported in `results.json`.

Collision events record their start and end times, impulse counts, peak impulse, initial normal speed and modeled kinetic energy loss. Adjacent contact impulses within 0.2 s are grouped into an episode. Multiple impulses can represent rocking or sustained contact.

This is an illustrative rigid contact model. It omits structural damage, fracture, contact friction, detailed face contact manifolds, tether snagging and entanglement. It does not claim that real CubeSats would remain intact after all contacts. The modeled bodies remain intact and continue moving.

## Detailed deployment implementation

Based on [scenarioFormationBasic](https://avslab.github.io/basilisk/examples/scenarioFormationBasic.html) and [scenarioConstrainedDynamics](https://avslab.github.io/basilisk/examples/scenarioConstrainedDynamics.html).

Both buses are native Basilisk `Spacecraft` objects. RK4 integration is synchronized. The same native Earth J2 model acts on both. Compiled attachment calculations provide the next interval's spring and tether forces through `ExtForceTorque`, including rotational effective mass and attachment torques. The scalar force solve uses an implicit midpoint step. Force directions and torques are sampled at the integration interval rather than recomputed at every RK4 stage.

Collision impulses are applied directly to those same hub states. Updated states are published before recording and before the next integration interval. Neither spacecraft is replaced by a reference object.

Vizard replays the actual Earth centered inertial states and attitudes. A camera reference follows their COM. The orbit and close-up have one timestamp and one trajectory. No separate pre-release orbit or artificial orbital translation is used.

Both displayed buses and all tether segments share `Deployment_center` as their Vizard display parent. This keeps meter scale offsets consistent in the orbit view's instrument camera. Their messages retain the original inertial positions and attitudes. Parenting affects visualization only.

The visible tether uses 32 independently posed native cuboid segments. Its slack loop is schematic, since transverse tether dynamics are omitted. Display thickness is 4 mm for visibility. A 1% segment overlap closes the joints. These display choices do not change the physical 0.5 mm nylon or the simulated forces.

Drag uses a medium activity NRLMSISE-00 density table, averaged over seasons and local solar times. Each hub receives a force based on its actual altitude and velocity relative to co-rotating air. The pair's mean projected area is split equally between the hubs. The assumed drag coefficient is 2.2. Forces act at the hub centers. Drag torque and atmospheric winds are omitted. `--no-drag` preserves the original gravity and tether regression model.

Other omitted physics include individual bus gravity gradient torque, tether mass and bending, creep, knots and breakage. Differential Earth acceleration between the hubs is included. Inelastic contact dissipates energy. No external braking force is applied.

## Checks

```bash
.venv/bin/python -m unittest discover -s tether-simulation -v
```

Checks cover the analytical free space limit, tension only behavior, native J2 gravity, energy and nodal precession, impulse restitution and momentum, oriented contact geometry, continued motion through impacts, agreement of the COM with an independent J2 validation orbit, and native Vizard replay of the actual post-impact states. The independent validation orbit is used only in tests and is never substituted into the deployment visualization.

Lifetime checks cover the analytical constant density drag limit, zero drag over eight years, the mission phase transition, optional stationkeeping, integration step convergence, native atmosphere sampling and the altitude stop boundary.

Streaming checks compare the live trajectory with the original in-memory integration, including release and actual impacts. They verify drag work against the orbital energy change, agreement of CSV and native Vizard states, display geometry, complete event logging and atomic publication of completed files.
