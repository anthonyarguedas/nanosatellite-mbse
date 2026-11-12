# GUI Python backend

The backend belongs to `framework.gui`.
`framework.models` is the independent public Python API.
The GUI retains its existing workbook model under `legacy/` until its editors migrate.
Workbook persistence lives in `legacy/persistence/`.
The new Mission classes have no browser schema or storage protocol.

## Modules

- `application.py`: session operations, independent browser drafts and execution evidence handles.
- `edits.py`: apply browser changes to native model objects.
- `validation.py`: bounded JSON transport validation.
- `views.py`: workbook metadata projected from compatibility objects.
- `legacy/`: the old workbook model, expression engine and storage adapters.
- `__main__.py`: JSON-lines transport, cancellation and bounded requests.
- `service.py`: source bootstrap used by the Node server, including isolated Python mode.

The normal launcher is `npm start --prefix framework/gui` from the repository root.
The Node server starts `backend/service.py` with `python3 -I -B -u`.
Installed deployments can launch `python3 -I -m framework.gui.backend`.

The service accepts `--model`, `--sessions` and `--cots-directory` as trusted local launch settings.
Requests carry model operations and opaque draft/evidence handles.
Requests cannot configure import paths or launch arbitrary source files.
The default script registry is empty while analyses are being refactored.

The existing transport protocol and workbook behavior are retained.
Live validation should use temporary sessions to avoid changing an active workspace.
