# GUI backend

This package adapts browser requests to `framework.models`.
It contains no engineering model or expression interpreter.

- `application.py` manages session handles and atomic edit transactions.
- `edits.py` calls public model methods and records equivalent Python source.
- `views.py` formats `assess()`, `render_statement()`, `verify()` and `recommend_cots()` results.
- `repository.py` loads trusted Python sessions and saves source with revision checks.
- `__main__.py` provides JSON-lines transport.
- `service.py` launches the source checkout from the Node server.

The browser stores unsaved editor drafts.
Preview requests copy the Mission while retaining its imported module interfaces.
They apply the same model calls used by Save and discard the copy afterward.
A failed transaction leaves the live Mission and saved source unchanged.
Read-only recommendation requests pass the session's `cots_catalog` to the public model query.

Session files and expressions execute trusted Python with user permissions.
There is no restricted interpreter, subprocess analysis runner or GUI compliance policy.
The HTTP server accepts only local, same-origin requests.
File paths come from launcher configuration and generated session IDs.

Use `python3 -m framework.gui.backend` for JSON-lines access.
Optional launcher arguments are `--model` and `--sessions`.
The normal browser launcher is `npm start --prefix framework/gui`.
