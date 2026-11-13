"""Trusted Python session loading and revision-checked source storage."""

import ast
from contextlib import contextmanager
from hashlib import sha256
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from types import ModuleType
from uuid import uuid4

from framework.models import Mission


class Conflict(ValueError):
    status = 409


def revision(source):
    return sha256(source.encode("utf-8")).hexdigest()


def package_context(directory):
    packages = [path for path in (directory, *directory.parents) if (path / "__init__.py").is_file()]
    if not packages:
        return "", directory
    root = packages[-1].parent
    return ".".join(directory.relative_to(root).parts), root


@contextmanager
def source_directory(directory):
    previous = sys.path[:]
    _, root = package_context(directory)
    sys.path[:0] = [str(directory), str(root)]
    try:
        yield
    finally:
        sys.path[:] = previous


def load(path):
    source = path.read_text(encoding="utf-8")
    module = ModuleType(f"_gui_session_{uuid4().hex}")
    module.__file__ = str(path)
    module.__package__ = package_context(path.parent)[0]
    sys.modules[module.__name__] = module
    try:
        with source_directory(path.parent):
            exec(compile(source, str(path), "exec"), module.__dict__)
            mission = module.__dict__.get("mission")
            assignment = ""
            if not isinstance(mission, Mission):
                matches = [(name, value) for name, value in vars(module).items() if isinstance(value, Mission)]
                factory = module.__dict__.get("build_mission")
                if matches:
                    if len({id(value) for _, value in matches}) != 1:
                        raise ValueError("Choose one configuration as mission.")
                    name, mission = matches[0]
                    assignment = f"mission = {name}\n"
                elif callable(factory):
                    mission = factory()
                    assignment = "mission = build_mission()\n"
                else:
                    raise ValueError("A session must define mission or build_mission().")
            if not isinstance(mission, Mission):
                raise TypeError("build_mission() must return a framework.models.Mission.")
        return mission, source, assignment, module
    except Exception:
        sys.modules.pop(module.__name__, None)
        raise


def append_calls(source, assignment, calls):
    """Keep authored definitions and place ordinary API calls before CLI output."""
    tree = ast.parse(source)
    position = len(source)
    lines = source.splitlines(keepends=True)
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            test = node.test
            operands = (test.left, *test.comparators)
            if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq) and any(
                isinstance(item, ast.Name) and item.id == "__name__" for item in operands
            ) and any(isinstance(item, ast.Constant) and item.value == "__main__" for item in operands):
                position = sum(len(line) for line in lines[:node.lineno - 1])
                break
    imported = any(isinstance(node, ast.Import) and any(
        alias.name == "framework.models" and alias.asname == "_gui_models" for alias in node.names
    ) for node in tree.body)
    model_import = "import framework.models as _gui_models\n" if not imported and any("_gui_models." in call for call in calls) else ""
    block = "\n" + assignment + model_import + "\n".join(calls) + "\n\n"
    result = source[:position].rstrip() + "\n" + block + source[position:]
    compile(result, "<saved session>", "exec")
    return result


def anchored_copy(source, origin, package=""):
    """Keep a copied session's relative resources and helper imports usable."""
    nodes = ast.parse(source).body
    line = 0
    for index, node in enumerate(nodes):
        if (index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)) or (
                isinstance(node, ast.ImportFrom) and node.module == "__future__"):
            line = node.end_lineno
        else:
            break
    lines = source.splitlines(keepends=True)
    _, root = package_context(origin.parent)
    context = f"\n__file__ = {str(origin)!r}\n__package__ = {package!r}\nimport sys as _gui_sys\n_gui_sys.path[:0] = [{str(origin.parent)!r}, {str(root)!r}]\n\n"
    return "".join(lines[:line]) + context + "".join(lines[line:])


def save(path, source, expected=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(path.suffix + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Conflict("This session is being saved by another process. Try again.") from None
    temporary = None
    try:
        os.close(descriptor)
        actual = revision(path.read_text(encoding="utf-8")) if path.exists() else None
        if actual != expected:
            raise Conflict("The session changed on disk. Reopen it before saving.")
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(source)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)
    return revision(source)
