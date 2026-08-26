# Web of Science X03 setup incident

- **Session:** `S-D02-X03-20260826T012525-0400`
- **Mode:** X exploration allocation; deterministic setup failure before browser/source action
- **Source phase started:** false
- **Source navigations/submits/reissues:** 0 / 0 / 0

The new X-only runner exited 2 during local argument/configuration validation before connecting to CDP, creating an owned page, or navigating Web of Science. The defect used `type(PosixPath) is Path` instead of `isinstance(..., Path)`. No source condition, total, zero, control, or accessibility conclusion is inferred.

The one-line behavior-preserving correction is committed at `37212ec`; a create-only dry run, receipt assertions, `py_compile`, and `git diff --check` passed. X03 is not a route attempt and freezes no evidence plan. The next runtime X must use a new ID and the corrected runner.

The outer wrapper still acquired and released the canonical lease, reported `cleanup=verified-clean`, preserved one inert anchor, and found no orphan. Exact-window checks found no Sleep/Wake/DarkWake or System Information/About This Mac launch. No screening, import, gate, record, or final event occurred.
