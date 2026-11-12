# Workbook compatibility

This package preserves the existing GUI workbook and its version 1 Python sessions.
It is internal to `framework.gui.backend`.
It is separate from the new public model API in `framework.models`.

The GUI still uses its existing tables, lifecycle, expression interpreter and storage adapters.
They remain here until the GUI adopts the new Mission classes.
The public model library imports none of this code.

The source loader redirects canonical version 1 imports from `framework.models` to this package in memory.
Saved source files are left unchanged on load.
New GUI saves use the compatibility classes' actual import paths.
Legacy JSON conversion retains unavailable script interfaces without restoring their implementations.

Use `framework.models` for new Python models.
Use the GUI for existing workbooks.
This compatibility package is an explicit migration boundary.
