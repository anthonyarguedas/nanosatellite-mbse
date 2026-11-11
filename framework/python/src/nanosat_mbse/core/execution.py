"""Explicit, Python-owned analysis execution and immutable transient evidence.

Default execution uses an isolated subprocess with time, output and cancellation
limits. These limits reduce accidental resource use. Trusted Python still runs
with the user's permissions and is not sandboxed.
"""

from __future__ import annotations

import json
import os
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .identity import ALL_MODES
from .predicates import PendingValue


class ExecutionFailure(ValueError):
    def __init__(self, message, log=""):
        super().__init__(message)
        self.log = log


class ExecutionCancelled(ExecutionFailure):
    pass


class ExecutionLimit(ExecutionFailure):
    pass


class CancellationToken:
    def __init__(self):
        self._event = threading.Event()

    def cancel(self):
        self._event.set()

    def is_set(self):
        return self._event.is_set()


def _cancelled(cancel):
    if cancel is None:
        return False
    if callable(cancel):
        return bool(cancel())
    if hasattr(cancel, "is_set"):
        return bool(cancel.is_set())
    return bool(getattr(cancel, "aborted", False))


def _check_cancel(cancel):
    if _cancelled(cancel):
        raise ExecutionCancelled("Python execution was cancelled.")


def run_key(script, mode=None):
    key = script if isinstance(script, str) else script.key
    mode_key = mode if isinstance(mode, str) else None if mode is None else mode.key
    return f"{key}:{mode_key or ''}"


@dataclass(frozen=True)
class ExecutionResult:
    script: str
    mode: object
    revision: str
    implementation_revision: str
    state: str
    values: Mapping = field(default_factory=dict)
    inputs: Mapping = field(default_factory=dict)
    log: str = ""
    message: str = ""
    executed_at: object = None
    duration_ms: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))

    def projection(self):
        return {
            "script": self.script,
            "mode": self.mode,
            "revision": self.revision,
            "implementationRevision": self.implementation_revision,
            "state": self.state,
            "values": dict(self.values),
            "inputs": dict(self.inputs),
            "log": self.log,
            "message": self.message,
            "executedAt": self.executed_at,
            "durationMs": self.duration_ms,
        }


@dataclass(frozen=True)
class ExecutionEvidence:
    signature: str
    cots_signature: object
    runs: Mapping = field(default_factory=dict)

    def __post_init__(self):
        if any(not isinstance(value, ExecutionResult) for value in self.runs.values()):
            raise TypeError("Evidence contains immutable ExecutionResult records.")
        object.__setattr__(self, "runs", MappingProxyType(dict(self.runs)))

    def result_for(self, script, mode=None):
        return self.runs.get(run_key(script, mode))

    def projection(self):
        return {
            "signature": self.signature,
            "cotsSignature": self.cots_signature,
            "runs": {
                identity: result.projection() for identity, result in self.runs.items()
            },
        }

    @property
    def successful(self):
        return bool(self.runs) and all(
            result.state == "value" for result in self.runs.values()
        )


class IsolatedRunner:
    """Bounded subprocess invocation of the same importable calculation classes."""

    def __init__(self, *, python=None, max_output_bytes=1048576):
        self.python = sys.executable if python is None else os.fspath(python)
        if type(max_output_bytes) is not int or max_output_bytes < 1:
            raise ValueError("The output limit must be a positive byte count.")
        self.max_output_bytes = max_output_bytes

    def invoke(self, script, payload, *, timeout_ms, cancel=None):
        _check_cancel(cancel)
        with tempfile.TemporaryDirectory(prefix="nanosat-verification-") as directory:
            if hasattr(script, "registered_source"):
                registered = script.registered_source()
                target = Path(directory) / "analysis.py"
                target.write_text(registered.source, encoding="utf-8")
                target.chmod(0o600)
                request = payload
            else:
                cls = type(script)
                if cls.__module__ == "__main__" or "<locals>" in cls.__qualname__:
                    raise ValueError(
                        "Isolated analyses need an importable class. Use InlineRunner explicitly for a trusted interactive class."
                    )
                target = Path(__file__).with_name("_script_process.py")
                request = {
                    **payload,
                    "classModule": cls.__module__,
                    "className": cls.__qualname__,
                    "definition": script.definition,
                    "implementationRevision": script.current_revision,
                }
            encoded = json.dumps(request, allow_nan=False).encode("utf-8")
            if len(encoded) > 8 * 1024 * 1024:
                raise ExecutionLimit("The Python invocation exceeds 8 MiB.")
            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": directory,
                "LANG": "en_US.UTF-8",
                **(
                    {"SystemRoot": os.environ["SystemRoot"]}
                    if "SystemRoot" in os.environ
                    else {}
                ),
            }
            process = subprocess.Popen(
                [self.python, "-I", "-B", "-u", str(target)],
                cwd=directory,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=os.name != "nt",
                bufsize=0,
            )
            return self._communicate(process, encoded, timeout_ms, cancel)

    @staticmethod
    def _kill(process):
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def _communicate(self, process, payload, timeout_ms, cancel):
        # Bounded queues keep eager child output from accumulating in memory.
        # Threads also permit cancellation while a script refuses stdin.
        events = queue.Queue(maxsize=16)
        stopping = threading.Event()
        threads = []

        def publish(item):
            while not stopping.is_set():
                try:
                    events.put(item, timeout=0.05)
                    return
                except queue.Full:
                    continue

        def read(stream, label):
            try:
                while not stopping.is_set():
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    publish((label, chunk))
            finally:
                publish((label, None))

        def write():
            try:
                remaining = memoryview(payload)
                while remaining and not stopping.is_set():
                    count = process.stdin.write(remaining)
                    if not count:
                        break
                    remaining = remaining[count:]
            except (BrokenPipeError, OSError, ValueError):
                pass
            finally:
                process.stdin.close()

        for target, args in (
            (read, (process.stdout, "out")),
            (read, (process.stderr, "err")),
            (write, ()),
        ):
            thread = threading.Thread(target=target, args=args, daemon=True)
            threads.append(thread)
            thread.start()
        deadline = time.monotonic() + timeout_ms / 1000
        chunks, size, ended = {"out": [], "err": []}, 0, set()
        descendants_cleaned = False
        try:
            while len(ended) < 2:
                _check_cancel(cancel)
                if time.monotonic() >= deadline:
                    raise ExecutionLimit(
                        f"Python execution timed out after {round(timeout_ms)} ms."
                    )
                if process.poll() is not None and not descendants_cleaned:
                    self._kill(process)
                    descendants_cleaned = True
                try:
                    label, chunk = events.get(
                        timeout=min(0.05, max(0.001, deadline - time.monotonic()))
                    )
                except queue.Empty:
                    continue
                if chunk is None:
                    ended.add(label)
                    continue
                size += len(chunk)
                if size > self.max_output_bytes:
                    raise ExecutionLimit(
                        f"Python output exceeded {self.max_output_bytes} bytes."
                    )
                chunks[label].append(chunk)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ExecutionLimit("Python execution timed out.")
            try:
                code = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                raise ExecutionLimit(
                    f"Python execution timed out after {round(timeout_ms)} ms."
                ) from None
            stdout = b"".join(chunks["out"]).decode("utf-8", errors="replace")
            stderr = b"".join(chunks["err"]).decode("utf-8", errors="replace")
            if code != 0:
                raise ValueError(
                    f"Python exited {code}: {stderr.strip()[-2500:] or 'No error details.'}"
                )
            try:
                values = json.loads(stdout)
            except (ValueError, TypeError) as error:
                raise ValueError(
                    f"Python must write one JSON object to stdout ({error})."
                ) from None
            if not isinstance(values, dict):
                raise ValueError("Python must write one JSON object to stdout.")
            return values, stderr.strip()[-8000:]
        except Exception as error:
            log = (
                b"".join(chunks["err"])
                .decode("utf-8", errors="replace")
                .strip()[-8000:]
            )
            if isinstance(error, ExecutionFailure):
                error.log = log
                raise
            raise ExecutionFailure(str(error), log) from error
        finally:
            stopping.set()
            self._kill(process)
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            for thread in threads:
                thread.join(timeout=0.2)
            for stream in (process.stdin, process.stdout, process.stderr):
                try:
                    stream.close()
                except (OSError, ValueError):
                    pass


class _CapturedOutput:
    def __init__(self, maximum):
        self.maximum, self.size, self.parts = maximum, 0, []

    def write(self, text):
        self.size += len(text.encode("utf-8"))
        if self.size > self.maximum:
            raise ExecutionLimit(f"Python output exceeded {self.maximum} bytes.")
        self.parts.append(text)
        return len(text)

    def flush(self):
        pass


class InlineRunner:
    """Explicit opt-in for trusted interactive classes and debugging.

    A running native function cannot be safely interrupted in process. Time and
    cancellation are checked before and after it, and output is bounded. The
    shared HTTP service should always use IsolatedRunner.
    """

    def __init__(self, *, max_output_bytes=1048576):
        self.max_output_bytes = max_output_bytes

    def invoke(self, script, payload, *, timeout_ms, cancel=None):
        _check_cancel(cancel)
        loaded = getattr(type(script), "_loaded_implementation_revision", None)
        if loaded is not None and loaded != script.current_revision:
            raise ValueError(
                "Reload the analysis class after editing its source before using InlineRunner."
            )
        captured = _CapturedOutput(self.max_output_bytes)
        start = time.monotonic()
        try:
            with redirect_stdout(captured), redirect_stderr(captured):
                values = script.calculate(
                    payload["inputs"],
                    requirements=payload["requirements"],
                    mode=payload["mode"],
                )
        except Exception as error:
            raise ExecutionFailure(
                str(error), "".join(captured.parts).strip()[-8000:]
            ) from error
        _check_cancel(cancel)
        if (time.monotonic() - start) * 1000 > timeout_ms:
            raise ExecutionLimit(
                f"Python execution exceeded {round(timeout_ms)} ms in InlineRunner."
            )
        return values, "".join(captured.parts).strip()[-8000:]


def run(
    session,
    script=None,
    *,
    mode=ALL_MODES,
    runner=None,
    evidence=None,
    cancel=None,
    total_timeout_ms=30000,
    reuse_dependencies=True,
):
    """Execute targets and needed dependencies, preserving configuration only."""
    from .evaluation import EvaluationContext, resolve_modes
    from .verification import VerificationScript

    if (
        type(total_timeout_ms) not in (int, float)
        or not 1 <= total_timeout_ms <= 300000
    ):
        raise ValueError("Use an execution budget from 1 through 300,000 ms.")
    if script is None:
        targets = tuple(session.scripts)
    elif isinstance(script, (list, tuple)):
        targets = tuple(session.get(item) for item in script)
    else:
        targets = (session.get(script),)
    if any(not isinstance(target, VerificationScript) for target in targets):
        raise TypeError(
            "Choose a VerificationScript instance registered in this session."
        )
    selected_modes = resolve_modes(session, mode)
    invocation = IsolatedRunner() if runner is None else runner
    context = EvaluationContext(session)
    signature, cots_signature = context.signature, context.cots_signature
    previous = (
        getattr(session, "_execution_evidence", None) if evidence is None else evidence
    )
    runs = {}
    if (
        reuse_dependencies
        and isinstance(previous, ExecutionEvidence)
        and previous.signature == signature
        and previous.cots_signature == cots_signature
    ):
        runs.update(
            (identity, result)
            for identity, result in previous.runs.items()
            if result.state == "value"
        )
    for target in targets:
        for selected in selected_modes:
            runs.pop(run_key(target, selected), None)
    active = set()
    deadline = time.monotonic() + total_timeout_ms / 1000

    def snapshot():
        return ExecutionEvidence(signature, cots_signature, runs)

    def ensure(target, selected):
        identity = run_key(target, selected)
        if identity in active:
            raise ValueError(f"Cyclic Python dependency at {target.id}.")
        existing = runs.get(identity)
        if existing is not None:
            return existing
        active.add(identity)
        started = time.monotonic()
        inputs, values, log, executed_at = {}, {}, "", None
        implementation = target.current_revision
        state, message = "pending", ""
        try:
            _check_cancel(cancel)
            if time.monotonic() >= deadline:
                raise ExecutionLimit("The Python run exceeded its total time limit.")
            target.assert_current()
            for _ in range(len(session.scripts) + 1):
                try:
                    bound = session.script_inputs(
                        target, mode=selected, evidence=snapshot()
                    )
                    break
                except PendingValue as error:
                    if error.script_key is None:
                        raise
                    dependency = session.get(error.script_key)
                    if run_key(dependency, selected) in runs:
                        raise
                    ensure(dependency, selected)
            else:
                raise ValueError("Could not resolve analysis dependencies.")
            if (
                bound["signature"] != signature
                or bound["cotsSignature"] != cots_signature
            ):
                raise PendingValue(
                    "Calculation inputs or selected catalogue facts changed during execution. Run again."
                )
            inputs = target.validate_inputs(bound["inputs"])
            remaining_ms = (deadline - time.monotonic()) * 1000
            if remaining_ms <= 0:
                raise ExecutionLimit("The Python run exceeded its total time limit.")
            payload = {
                "inputs": inputs,
                "requirements": bound["requirements"],
                "mode": None
                if selected is None
                else {"key": selected.key, "name": selected.name},
            }
            raw_values, log = invocation.invoke(
                target,
                payload,
                timeout_ms=min(target.spec.timeout_ms, remaining_ms),
                cancel=cancel,
            )
            values = target.validate_outputs(raw_values)
            _check_cancel(cancel)
            if (
                target.current_revision != implementation
                or not target.revision_is_current
            ):
                raise PendingValue(
                    "The analysis implementation changed during execution. Review and run again."
                )
            current = EvaluationContext(session)
            if (
                current.signature != signature
                or current.cots_signature != cots_signature
            ):
                raise PendingValue(
                    "Calculation inputs or selected catalogue facts changed during execution. Run again."
                )
            state, message = (
                "value",
                "Python execution completed for the current inputs.",
            )
            executed_at = datetime.now(timezone.utc).isoformat()
        except PendingValue as error:
            state, message, values = "pending", str(error), {}
        except Exception as error:
            state, message, values = "error", f"{type(error).__name__}: {error}", {}
            log = getattr(error, "log", log)
        finally:
            active.remove(identity)
        result = ExecutionResult(
            target.key,
            None if selected is None else selected.key,
            target.revision,
            implementation,
            state,
            values,
            inputs,
            log,
            message[:2500],
            executed_at,
            (time.monotonic() - started) * 1000,
        )
        runs[identity] = result
        return result

    for selected in selected_modes:
        for target in targets:
            ensure(target, selected)
    result = snapshot()
    session._execution_evidence = result
    return result
