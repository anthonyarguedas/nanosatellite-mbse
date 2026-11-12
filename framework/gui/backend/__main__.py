"""Bounded JSON-lines transport for the native application service.

Launch configuration is trusted local input. Request data contains no filesystem
paths, interpreter arguments or source-loading operations. A reader thread can
cancel active native analysis execution while the serial application job runs.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path

from ...models.execution import CancellationToken
from .application import Application, ServiceError

MAX_REQUEST = 8 * 1024 * 1024
MAX_RESPONSE = 16 * 1024 * 1024


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        type=Path,
        help="Current session file (defaults to sessions/current.py).",
    )
    parser.add_argument("--sessions", type=Path)
    parser.add_argument("--cots-directory", type=Path)
    args = parser.parse_args(argv)
    output = sys.stdout
    output_lock = threading.Lock()
    active_lock = threading.Lock()
    active = {}
    stopping = threading.Event()
    application = Application(
        args.model,
        session_directory=args.sessions,
        cots_directory=args.cots_directory,
    )

    def respond(identity, *, result=None, error=None):
        packet = (
            {"id": identity, "error": error}
            if error is not None
            else {"id": identity, "result": result}
        )
        try:
            encoded = (
                json.dumps(
                    packet, ensure_ascii=True, allow_nan=False, separators=(",", ":")
                )
                + "\n"
            )
            if len(encoded.encode("utf-8")) > MAX_RESPONSE:
                raise ValueError("Python service response exceeded 16 MiB.")
        except (TypeError, ValueError) as failure:
            encoded = (
                json.dumps(
                    {"id": identity, "error": {"message": str(failure), "status": 503}}
                )
                + "\n"
            )
        with output_lock:
            try:
                output.write(encoded)
                output.flush()
            except (BrokenPipeError, OSError):
                stopping.set()

    def execute(request, cancel):
        identity = request["id"]
        try:
            if stopping.is_set() or cancel.is_set():
                raise ServiceError("The request was cancelled.", 499)
            with redirect_stdout(sys.stderr):
                result = application.dispatch(request, cancel=cancel)
            respond(identity, result=result)
        except Exception as error:
            status = getattr(
                error,
                "status",
                404
                if isinstance(error, FileNotFoundError)
                else 400
                if isinstance(error, (ValueError, TypeError, KeyError, SyntaxError))
                else 500,
            )
            if status == 500:
                traceback.print_exc(file=sys.stderr)
            respond(
                identity,
                error={
                    "message": str(error),
                    "status": status,
                    "pending": type(error).__name__ == "PendingValue",
                    "scriptKey": getattr(error, "script_key", None),
                },
            )
        finally:
            with active_lock:
                active.pop(identity, None)

    def stop(*_):
        # Unwind reader locks first. Cancellation in the finally block then
        # wakes the native runner without acquiring locks in a signal handler.
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    executor = ThreadPoolExecutor(
        max_workers=1, thread_name_prefix="nanosat-application"
    )
    try:
        while not stopping.is_set():
            raw = sys.stdin.buffer.readline(MAX_REQUEST + 1)
            if not raw:
                break
            if len(raw) > MAX_REQUEST:
                while raw and not raw.endswith(b"\n"):
                    raw = sys.stdin.buffer.readline(MAX_REQUEST + 1)
                respond(
                    None,
                    error={
                        "message": "Python service request exceeds 8 MiB.",
                        "status": 413,
                    },
                )
                continue
            request = None
            try:
                request = json.loads(
                    raw,
                    parse_constant=lambda value: (_ for _ in ()).throw(
                        ValueError(f"Nonfinite JSON value {value}.")
                    ),
                )
                if not isinstance(request, dict):
                    raise ValueError("Send one request object per line.")
                if "cancel" in request:
                    with active_lock:
                        tokens = (
                            tuple(active.values())
                            if request["cancel"] == "all"
                            else (active.get(request["cancel"]),)
                        )
                    for token in tokens:
                        if token is not None:
                            token.cancel()
                    continue
                identity = request.get("id")
                if type(identity) is not int or identity < 1:
                    raise ValueError("Requests need positive integer IDs.")
                with active_lock:
                    if identity in active or len(active) >= 17:
                        raise ServiceError(
                            "The Python service queue is full or the ID is active.", 429
                        )
                    cancel = CancellationToken()
                    active[identity] = cancel
                executor.submit(execute, request, cancel)
            except Exception as error:
                respond(
                    request.get("id")
                    if isinstance(locals().get("request"), dict)
                    else None,
                    error={
                        "message": str(error),
                        "status": getattr(error, "status", 400),
                    },
                )
    except KeyboardInterrupt:
        pass
    finally:
        stopping.set()
        with active_lock:
            for cancel in active.values():
                cancel.cancel()
        executor.shutdown(wait=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
