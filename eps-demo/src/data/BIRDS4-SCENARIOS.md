# BIRDS-4 scenario basis

The example is a **BIRDS-4-inspired concept study**, not a reconstructed flight EPS or a replay of flight telemetry. COTS alternatives in this demo are not claimed to have flown on BIRDS-4.

## Source

H. R. Shrestha, BIRDS-4 Project Members, G. Maeda, S. Kim, H. Masui, T. Yamauchi and M. Cho, *BIRDS-4 1U CubeSat Missions and On-Orbit Results*, 11th Nano-Satellite Symposium, 2022.

Public conference PDF: <https://nanosat11th.itu.edu.tr/assets/papers/BIRDS-4.pdf>. Retrieved successfully on 2026-10-17. SHA-256: `e344753dac510b9e42ff70cd455dcfb72e2168ceb15bfc25d15c1f0bc1cebcaf`.

The source is also present in the user's local corpus as citation candidate 2055. The full six-page text was read, including the distinctions between planned activities, demonstrated operations and failed payload exchanges.

## Sourced context

- BIRDS-4 comprised GuaraniSat-1, Maya-2 and Tsuru, three 1U CubeSats deployed from the ISS on 14 March 2021 (§§1–2).
- Its mission list includes camera imaging, APRS digipeating, store and forward, Hentenna, radiation and latch-up experiments, perovskite solar-cell measurements and attitude demonstrations (§3).
- The bus includes OBC, EPS, communications, front/rear access boards and mission boards (§4).
- The camera section discusses imaging at 400 km altitude (§5.1). The demo uses **400 km as a representative circular reference altitude**, not a precise historical orbit, epoch or complete ISS deployment state. The one-year design lifetime is a demo assumption.
- The paper reports a power-budget imbalance in its generation-shortfall discussion (§5). This motivates a separate reduced-generation example. Its reported 1604, 1202 and 1438 mWh figures are not copied into a simulation boundary or interval that the demo has not independently established.
- APRS was demonstrated. The SF-WARD flight data exchange failed because of the reported packet-mode mismatch (§§5.2–5.3). The demo's combined APRS/SF-WARD row represents planned operations, not a claim of successful SF-WARD flight service.
- The ADCS section reports reaction-wheel activations of one through four minutes on different dates, while several stabilization/pointing functions were not activated (§5.6). The example's actuator windows are illustrative. They do not claim simultaneous historical operations or working closed-loop pointing.

## Authored numerical assumptions

Every component power, idle state, supply-rail assignment, phase window, duty cycle, simultaneous demand, illumination multiplier, initial energy, energy reserve and assessment duration in `scenarios.ts` is an editable **demonstration assumption**. No per-mode measured BIRDS-4 load table was established for these values.

Default source power, battery capacity, retention, efficiencies, DoD, limits, mass allocation and lifetime are also study assumptions. They do not represent the original BIRDS-4 NiMH pack, solar installation or charger. The source's hardware identities are retained as context and are not silently substituted with unrelated catalog revisions.

The three cases are routine scheduled operations, hypothetical overlapping mission demand, and reduced-generation essential service. Automatic mode transitions, shedding decisions and recovery are outside this demo. All schedules can be edited graphically or numerically before reevaluation.
