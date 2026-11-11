# Native Python sessions

The authoritative file contains imports, populated domain objects and explicit verification calls.
It contains no copied COTS values, execution outputs or verification success flags.
The browser projection remains a transport view.

## Creation and reuse

`Session()` creates an empty model with no added elements or requirements.
The UI's New session action uses this constructor.
A missing default workspace also starts blank when no native metadata or legacy source exists.
Add domain objects through `Session.add()` to run their normal initialization methods.
Reuse a saved session by opening it and choosing Save as in the UI, or saving the loaded graph to a new native path.
The supplied Generic EPS Example is a normal saved file with no special creation or regeneration behavior.

## Storage locations

The UI and CLI use `framework/sessions/current.py` as their default workspace in a source checkout.
Named sessions live directly under `framework/sessions/<id>/`, alongside the current workspace.
The supplied Generic EPS Example is one of these ordinary saved sessions.
Outside a checkout, the default workspace is `sessions/current.py` under the working directory.
A custom workspace uses a neighboring `sessions/` directory for named sessions.
When the workspace is already inside a directory named `sessions`, that directory is reused.
The service's `--sessions` argument selects an explicit named-session directory.

## Native API

```python
from nanosat_mbse import Session

session = Session.open("framework/sessions/current.py")
period = session.value("ORB001", "orbit_period_s")
session.get("ORB001").set_value("altitude_km", 500)
session.run("SCR001")
checks = session.verify()
status = session.save()
print(status.path, status.revision)
```

`Session.open()` loads trusted Python source and calls `build_session()`.
It leaves the generated `run_verifications()` entry point unexecuted.
Execution evidence starts empty.
`Session.open()` and `reload()` apply the same idempotent default reconciliation as the UI.
This adds newly available generic obligations in memory while preserving recorded deletions.
The stored source stays unchanged until a save.
`SessionRepository.load()` and `loads()` remain exact restoration APIs without this editing preparation.
`Session.save()` returns an immutable `StorageStatus` and attaches it to `session.storage`.
A new session requires a destination path.
Saving to an existing path requires its current revision.
A loaded session supplies its last successful revision automatically.
Saving to a new path attaches the same live graph to the new independent file.

`session.reload()` returns a fresh graph and leaves the current graph unchanged.
Use `session = session.reload()` and obtain object references from that refreshed graph.
This keeps older references from silently changing identity.

The shared `SessionRepository` supplies `load()`, `save()` and create-only `create()`.
Pass configured `catalog`, `database` and `verification_registry` providers to the repository or `Session.open()`.
An installed package needs its COTS directory through `TabularDatabase(directory)` or `NANOSAT_MBSE_COTS_DIR`.
Session files retain product IDs and fact pins, with values resolved from the current provider.

## Source structure

Generated files have a `SESSION_FORMAT = 1` marker and this shape:

```python
from nanosat_mbse.core.requirements import Parameter
from nanosat_mbse.core.session import Session
from nanosat_mbse.verifications.normal_interval import NormalInterval

SESSION_FORMAT = 1


def build_session(*, catalog=None, database=None, verification_registry=None):
    session = Session(
        name="An example",
        catalog=catalog,
        database=database,
        verification_registry=verification_registry,
    )
    analysis = session.restore(NormalInterval(
        id="SCR001",
        parameters=(
            Parameter("mean", value=4),
            Parameter("standard_deviation", value=1),
            Parameter("confidence", value=0.95),
        ),
    ))
    return session


def run_verifications(session, **execution_options):
    return session.run((session.get("SCR001"),), **execution_options)


if __name__ == "__main__":
    session = build_session()
    evidence = run_verifications(session)
```

The full generated file also preserves identities, declared ports and revisions, requirement subclasses, metadata, relationships, component states, mode allocations and initialization history.
`Session.restore()` registers explicitly constructed instances without default creation hooks.
The class `restore()` methods preserve concrete inheritance while bypassing initialization defaults.
`restore_roots()` installs the concrete Mission and External instances together.
`restore_state()` restores typed seed history and deletion markers after relationships are connected.
Use normal constructors and `Session.add()` when creating new engineering objects.

`dumps(session)` and `loads(source)` are available from `nanosat_mbse.persistence` for trusted in-memory source round trips.
They never evaluate parameter expressions or run analysis scripts.
Source generation validates that every configured class and native callable has an importable identity.
Lambdas, closures, bound instance methods and functions defined only in a REPL fail clearly before a file is replaced.
Move reusable functions into an importable library module before saving them as bindings.

Additional attributes on custom classes require explicit `session_state_fields` declarations.
Their values must be supported literals, importable callables or references to registered objects.
A custom class can override its `restore()` hook when restoring additional state needs specialized behavior.
Unknown instance attributes fail serialization so they cannot be silently dropped or mistaken for configuration.
Keep transient service caches outside the domain graph.

The source writer regenerates the supported canonical configuration and standard execution entry point.
Arbitrary additional code in a handwritten file is outside this round-trip contract.
A trusted file without the format marker can be opened but is read-only for replacement.
Save it to a new `.py` path to preserve its original source.

## Storage integrity

Revision tokens cover the canonical path and exact file contents.
Tokens from another file cannot authorize replacement.
The repository rejects stale revisions, symbolic links, non-regular files, unsupported source and files larger than 16 MiB.
Filesystem aliases through parent directories normalize to the same file identity.

Before publication, the repository reconstructs the generated configuration and checks its canonical round trip.
Unrestorable state fails before the original file is replaced.
Saves use a per-file lock, a temporary file, filesystem synchronization and atomic publication.
Existing permissions are retained.
New files use create-only publication and start with permissions `0600`.
Browser and REPL writers share these rules.
A conflict leaves local edits in memory and the existing file intact.
Reload the current file or save to a new path for recovery.

The lock records its process ID and creation time.
A lock left after a crash requires manual review.
Remove it only after confirming that its owning process has stopped.
The repository never automatically removes an existing lock.

Python session files and imported modules run with the user's permissions.
Loading trusted Python is not a sandbox and can execute arbitrary code if the file has been edited to do so.
The generated structure keeps analysis execution behind the explicit entry point.
Never expose source loading or filesystem paths as an unrestricted browser endpoint.

## Explicit JSON migration

```sh
PYTHONPATH=framework/python/src python3 -m nanosat_mbse.persistence \
  framework/requirements-ui/demo/analysis-workspace.json \
  --output /tmp/my-analysis/session.py
```

Conversion creates a new file and leaves the original JSON untouched.
An existing destination produces a conflict.
It preserves the source graph without rerunning initialization hooks or analyses.
Use `--cots-directory` and `--scripts-directory` for explicit providers.
The script directory is trusted executable code.

The native API is `convert_json(source, destination, metadata=...)`.
Legacy metadata is optional.
It retains the session ID, name, template and creation time.
The returned `MigrationResult.metadata` names the new Python file and retains the legacy source filename.
Its `create(path)` method publishes new picker metadata without replacing any existing file.
The original metadata remains unchanged.
Metadata publication and model publication are separate explicit operations.
A service creating a named session should publish them inside its own new-session directory workflow.

`legacy_destination(path)` only suggests an adjacent `.py` path.
It performs no reads or writes.
The repository never automatically regenerates missing Python files or opens a legacy JSON file as Python.
The HTTP service can prefer an existing native sidecar or explicitly convert a legacy source once, with the original retained.
Those selection decisions belong in the service.

## Native callables in UI transport

A browser must never provide Python module paths for import.
A trusted service can project native bindings with a process-local `CallableRegistry`:

```python
from nanosat_mbse import CallableRegistry, Session

registry = CallableRegistry()
view = session.to_projection(callables=registry)
restored_view = Session.from_projection(view, callables=registry)
```

Parameter metadata carries an opaque `callable` descriptor.
Condition descriptors live in `modelState.verificationBindings`.
Descriptors contain a random token, a display label and `readOnly: true`.
Their expression cells are empty because no editable expression source represents the native function.
The UI should display the label and retain its read-only binding.
The registry resolves only previously registered trusted objects and never imports browser-supplied strings.
Unknown, expired or altered descriptors produce an error.
Each projected token is bound to its object and parameter or condition slot.
Moving a valid token to another row or binding is rejected.
A server restart requires a fresh projection.
Call `registry.clear()` when its trusted session handle closes.

The registry is a transport capability store, with no authority to execute arbitrary new functions.
Only trusted session loading or application composition should register values.
Replacing a native binding with expression source should be an explicit Python domain command.
Its response can remove the old descriptor and return a normal editable source cell.

The projection importer remains a compatibility adapter for known catalog types.
It does not encode arbitrary custom class constructors or additional subclass fields.
The service must retain the trusted native graph and apply edits through its methods.
For a detached draft clone that preserves custom inheritance, use the trusted `dumps()` and `loads()` boundary with the same providers.
Do not replace an authoritative custom session with a graph reconstructed solely from browser rows.
Execution evidence should likewise remain server-side behind opaque evidence tokens.
