# Archived pre-refactor checks

These files preserve the checks for the retired JavaScript domain model, JSON repositories and request-local Python worker.
Their original implementation dependencies have been removed.
The `.txt` suffix keeps Node from discovering them as current executable tests.
Use repository history when inspecting or reproducing that earlier architecture.

The active `npm test` command runs the retained requirement presentation checks in `../requirement-preview.test.mjs`.
It makes no claim of regression-suite parity for the native refactor.
Current behavior is exercised through the native examples, local HTTP probes and browser workflows documented in the application and Python package READMEs.
