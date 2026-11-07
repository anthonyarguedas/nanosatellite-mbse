# Requirements UI workflow example

- `requirements-workflow.mp4`: 6 minutes 30 seconds, 1080p, with slow pacing, deliberate pauses and one short phrase in the top left corner. No audio, side panels or added highlights.
- `example-workspace.json`: the EPS sizing, COTS, mass and volume example.
- `analysis-workspace.json`: the populated illumination and MPPT test bench.
- `poster.jpg`: video preview.

The walkthrough uses the same recorded UI with slower actions and longer pauses on inputs and results. Camera movements and edited transitions are slower. The transition from the power calculation to COTS selection includes the actual save and page scroll. Native UI focus indicators remain visible. Application source and example inputs are unchanged.

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

From `framework/requirements-ui/`:

```sh
MISSION_FILE=demo/example-workspace.json PORT=3002 npm start
```

For the analysis test bench, use `MISSION_FILE=demo/analysis-workspace.json` instead. Open <http://127.0.0.1:3002>. Open MPT008 in EPS and run SCR001 to execute MPPT and its illumination dependency.

To recreate the named test bench in the sizing example's Session picker:

```sh
node tools/create-analysis-session.mjs demo --mission demo/example-workspace.json
```

The app autosaves edits. Copy the example files first to preserve the recorded inputs.

## Recording observation

The scripts are demonstrated in the supplied standalone test bench. During recording, script outputs remained pending in the COTS-linked sizing session because `public/verification-editor.js` omitted the returned `cotsSignature` when merging execution evidence. The Python runs themselves completed. Application source was left unchanged.
