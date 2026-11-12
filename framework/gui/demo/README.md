# Requirements UI workflow example

> Historical recording and input fixtures. The old analyses, study factories and CLI have been removed.
> The JSON workspaces remain importable, with deleted analyses marked unavailable.
> See the [current framework guide](../../README.md) for library and GUI usage.

- `requirements-workflow.mp4`: 6 minutes 30 seconds, 1080p, with slow pacing, deliberate pauses and one short phrase in the top left corner. No audio, side panels or added highlights.
- `example-workspace.json`: the EPS sizing, COTS, mass and volume example.
- `analysis-workspace.json`: the populated illumination and MPPT test bench.
- `poster.jpg`: video preview.

The walkthrough uses the same recorded UI with slower actions and longer pauses on inputs and results. Camera movements and edited transitions are slower. The transition from the power calculation to COTS selection includes the actual save and page scroll. Native UI focus indicators remain visible. The video records the previous implementation, and its JSON inputs remain the reproducible baseline. The current UI uses the native Python model and session storage.

## Chapters

The video includes player chapter markers.

| Time | Topic |
| --- | --- |
| 00:00 | Orbit inputs |
| 00:25 | Two subsystems |
| 00:45 | Spacecraft modes |
| 01:10 | Component power states |
| 02:00 | Power budget |
| 02:35 | COTS selections |
| 03:05 | Catalogue facts |
| 03:40 | Battery mass |
| 04:00 | Battery volume |
| 04:20 | Spacecraft totals |
| 04:45 | Analysis test bench |
| 04:53 | Illumination analysis |
| 05:28 | MPPT analysis |
| 06:18 | Passing analysis checks |

## Workflow

1. Enter a circular orbit altitude of 500 km. The calculated period is 5,677 s.
2. Add exactly two subsystems, EPS and CDH, and exactly two modes, Nominal and Safe.
3. Define component states and calculate sunlight and eclipse load averages of 5.400 W and 3.600 W.
4. Select an AZUR SPACE 81441 solar cell and GomSpace NanoPower BPX 100 Wh battery, then link EPS requirements.
5. Select the battery's sourced mass, length, width and height facts in the COTS pane.
6. Reference those facts in the battery mass and volume requirements, then inspect their spacecraft rollups.
7. Select the illumination and MPPT test bench, run both example scripts, and inspect their outputs and passing checks.

## Demonstrated results

| Result | Value |
| --- | ---: |
| Battery nominal mass | 0.5000 kg |
| Battery rectangular envelope volume | 0.000327918 m³ |
| Example spacecraft mass | 0.7060 kg |
| Example spacecraft summed volume | 0.000402718 m³ |
| Longest sampled eclipse | 2,140 s |
| Mean panel irradiance | 853.1 W/m² |
| MPPT tracking efficiency | 0.9846 |
| MPPT delivered energy | 540.2 J |

All 15 orbit, illumination and MPPT checks pass in the test bench. Execution evidence remains transient and requires another run after reopening the file.

Power values and non-battery physical values are illustrative estimates. The selected battery facts are nominal catalogue values. The MPPT section and acceptance limits are synthetic test data. These examples establish preliminary calculation results. Hardware qualification, battery energy closure and mechanical fit require separate evidence. Unconfigured requirements remain pending.

## Open the examples

Prepare independent native copies from the repository root:

```sh
PYTHONPATH=framework/python/src python3 framework/python/examples/repl_demo.py \
  --prepare /tmp/nanosat-demo
cd framework/requirements-ui
MISSION_FILE=/tmp/nanosat-demo/sizing.py PORT=3002 npm start
```

Choose a new output directory because preparation uses create-only saves. Original JSON inputs and live COTS data remain unchanged.
For the analysis test bench, use `MISSION_FILE=/tmp/nanosat-demo/analysis.py` instead. Open <http://127.0.0.1:3002>. Open MPT008 in EPS and run SCR001 to execute MPPT and its illumination dependency.

To create another native named test bench in the sizing example's Session picker:

```sh
node tools/create-analysis-session.mjs demo --mission /tmp/nanosat-demo/sizing.py
```

This calls the native Python factory and shared repository. Creating a bench executes no analyses.
The app autosaves to the selected Python session. The primary download is executable Python configuration with no cached output literals.
A legacy `MISSION_FILE=demo/example-workspace.json` is still accepted, with its first open creating an adjacent authoritative `.py` file while retaining the JSON source.

## REPL demonstration

Use `python3 -i framework/python/examples/repl_demo.py --prepare /tmp/nanosat-repl-demo` with `PYTHONPATH=framework/python/src` from the repository root.
The REPL exposes native `session`, `sizing`, `eps`, `battery` and `mppt` objects.
Add `--run` for a rehearsal that calculates actual outputs, changes an input, demonstrates evidence invalidation, restores the binding, saves and reopens.
See the [REPL sequence and recording recipe](../../python/docs/repl.md).

## Recording observation

The scripts are demonstrated in the supplied standalone test bench. During that earlier recording, script outputs remained pending in the COTS-linked sizing session because the old `public/verification-editor.js` omitted the returned `cotsSignature` when merging execution evidence. The Python runs themselves completed, and application source was left unchanged during recording. The current native service uses scoped evidence tokens, and the migrated editor retains them.
