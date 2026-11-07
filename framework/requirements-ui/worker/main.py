"""Persistent JSON-lines worker. Every calculation uses a fresh model context."""
import json
import os
from pathlib import Path
import sys

# -I excludes the script directory. Only this trusted application directory is
# added, never a workspace or user-supplied module search path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluation import evaluate, script_inputs
from models import Pending, Workspace
from catalog import catalog, assess_requirement
from cots_data import product_facts

MAX_REQUEST = 8 * 1024 * 1024


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON number: {value}")


def main():
    while True:
        line = sys.stdin.buffer.readline(MAX_REQUEST + 1)
        if not line:
            return
        if len(line) > MAX_REQUEST:
            # A framing violation is fatal. The supervisor starts a fresh worker.
            print("Worker request exceeded 8 MiB.", file=sys.stderr, flush=True)
            return
        identifier = None
        request = result = response = None
        try:
            request = json.loads(line, parse_constant=reject_constant)
            identifier = request.get("id")
            operation = request.get("operation", "evaluate")
            if operation == "ping":
                result = {"pid": os.getpid(), "engine": "python"}
            elif operation == "evaluate":
                result = evaluate(request)
            elif operation == "script_inputs":
                result = script_inputs(request)
            elif operation == 'cots_facts':
                result = product_facts(request.get('product'))
            elif operation == 'cots_context':
                result = {'signature': Workspace.read(request.get('workspace')).cots_signature}
            elif operation == "catalog":
                result = catalog()
            elif operation == "catalog_assessment":
                result = assess_requirement(request.get("definition"), request.get("values", {}))
            else:
                raise ValueError("Unknown Python worker operation.")
            response = {"id": identifier, "result": result}
        except Exception as error:
            response = {"id": identifier, "error": {"message": str(error)[:2500], "pending": isinstance(error, Pending)}}
            if isinstance(error, Pending) and error.script_key:
                response["error"]["scriptKey"] = error.script_key
        print(json.dumps(response, allow_nan=False, separators=(",", ":")), flush=True)
        # Keep the interpreter and compiled syntax cache, never workspace values.
        request = result = response = None


if __name__ == "__main__":
    main()
