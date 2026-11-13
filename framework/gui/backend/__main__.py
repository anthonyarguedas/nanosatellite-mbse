"""JSON-lines transport for trusted local Python sessions."""

import argparse
from contextlib import redirect_stdout
import json
from pathlib import Path
import sys
import traceback

from .application import Application

MAX_REQUEST = 8 * 1024 * 1024
MAX_RESPONSE = 16 * 1024 * 1024


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--sessions", type=Path)
    args = parser.parse_args(argv)
    application = Application(args.model, session_directory=args.sessions)
    output = sys.stdout
    while True:
        raw = sys.stdin.buffer.readline(MAX_REQUEST + 1)
        if not raw:
            break
        request = None
        try:
            if len(raw) > MAX_REQUEST:
                while raw and not raw.endswith(b"\n"):
                    raw = sys.stdin.buffer.readline(MAX_REQUEST + 1)
                raise ValueError("Request exceeds 8 MiB.")
            request = json.loads(raw)
            if not isinstance(request, dict) or type(request.get("id")) is not int:
                raise ValueError("Send a request object with an integer ID.")
            with redirect_stdout(sys.stderr):
                result = application.dispatch(request)
            packet = {"id": request["id"], "result": result}
            encoded = json.dumps(packet, allow_nan=False)
            if len(encoded.encode("utf-8")) > MAX_RESPONSE:
                raise ValueError("Response exceeds 16 MiB.")
        except Exception as error:
            status = getattr(error, "status", 404 if isinstance(error, FileNotFoundError) else 400 if isinstance(error, (ValueError, TypeError, KeyError, AttributeError, SyntaxError)) else 500)
            if status == 500:
                traceback.print_exc(file=sys.stderr)
            encoded = json.dumps({"id": request.get("id") if isinstance(request, dict) else None,
                                  "error": {"message": str(error), "status": status}})
        output.write(encoded + "\n")
        output.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
