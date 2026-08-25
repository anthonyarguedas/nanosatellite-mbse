# Resume plan — S-D08-C01-20260825T132822-0400

> **Current architecture:** Follow the [two-mode source-interface policy](../../two-mode-validation-policy.md). PQDT returns to agent-driven exploration; do not allocate another immutable evidence attempt until the real route works.

**Status:** `technically_blocked`; P01 and P02 are immutable technical failures at the first field/thesaurus route. No query, total, record, screening, import, or final event occurred.

## Carries forward

- Exact nine source-native query files and translation algebra remain unchanged.
- Agent-tools commit `17a64bf` provides source-free count-only and strict two-pass contracts, but their live PQDT behavior is unvalidated.
- P01 exposed lost child diagnostics; the review runner/probe observability patch remains useful.
- P02 preserved `PQDTMetadataProtocolError` but the probe still collapsed the actual page state before source boundary/field evidence could be established.

## Next exploration session

1. Allocate `S-D08-X01-<timestamp>`, not P03.
2. In one owned page, use screenshots and bounded semantic DOM inspection on the normal PQDT database-selection and Command Line routes. Retain the exact selected database label, visible route/title, query input, submit, field/thesaurus controls, loading/access state, and the concrete adapter invariant that failed.
3. Patch the probe/adapter against the actual rendered page and retest live in the same exploration session with `TI("CubeSat")` count-only. Do not run all nine partitions during exploration.
4. Freeze the route, interaction recipe, selected database semantics, implementation commit, and expected count/zero evidence only after the sentinel works live.

## Later evidence attempt

After exploration succeeds, create a new deterministic evidence attempt using the existing 16-operation plan, or a smaller staged plan if the frozen live evidence supports it. Strict A1 runs only after count-only transport works and its natural total fits the predeclared bound.
