# GUI Python backend

The backend belongs to `framework.gui`.
`framework.models` remains independently usable as a Python library.
Session persistence lives in `framework/models/persistence/`.

## Modules

- `application.py`: session operations, independent browser drafts and execution evidence handles.
- `edits.py`: apply browser changes to native model objects.
- `validation.py`: bounded JSON transport validation.
- `views.py`: workbook metadata projected from model objects.
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
