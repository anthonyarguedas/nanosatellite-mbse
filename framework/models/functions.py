"""Explicit session imports and Property bindings for custom functions."""

import ast
import importlib
import inspect
from types import ModuleType
from typing import get_args, get_type_hints

from .properties import Property


class Function:
    """A named, annotated Python function returning an annotated NamedTuple."""

    def __init__(self, function):
        self.function = function
        self.signature = inspect.signature(function)
        self.annotations = get_type_hints(function)
        for name, parameter in self.signature.parameters.items():
            if parameter.kind not in (parameter.POSITIONAL_OR_KEYWORD, parameter.KEYWORD_ONLY):
                raise TypeError("Function inputs must have individually bindable names.")
            if name not in self.annotations:
                raise TypeError("Every Function input needs an annotation.")
            if type(None) in get_args(self.annotations[name]) and parameter.default is parameter.empty:
                raise TypeError("A nullable Function input needs an explicit default.")
        result = self.annotations.get("return")
        if not isinstance(result, type) or not issubclass(result, tuple) or not hasattr(result, "_fields"):
            raise TypeError("A Function returns an annotated NamedTuple.")
        fields = get_type_hints(result)
        if not result._fields or set(fields) != set(result._fields):
            raise TypeError("Every Function output needs a named, annotated field.")
        if any(type(None) in get_args(annotation) for annotation in fields.values()):
            raise TypeError("Function output annotations are nonoptional.")
        self.output_type = result

    @property
    def inputs(self):
        return {name: self.annotations[name] for name in self.signature.parameters}

    @property
    def outputs(self):
        return get_type_hints(self.output_type)

    def __call__(self, *args, **kwargs):
        bound = self.signature.bind(*args, **kwargs)
        if any(not isinstance(prop, Property) for prop in bound.arguments.values()):
            raise TypeError("Every supplied Function input must be explicitly bound to a Property.")
        values = {name: prop.value for name, prop in bound.arguments.items()}
        result = self.function(**values)
        if not isinstance(result, self.output_type):
            raise TypeError(f"The Function must return {self.output_type.__name__}.")
        return result


class ModuleImport:
    """A session's `import package as alias` and its callable interfaces."""

    def __init__(self, source):
        tree = ast.parse(source)
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Import):
            raise ValueError("Use import package as alias.")
        names = tree.body[0].names
        if len(names) != 1 or names[0].asname is None:
            raise ValueError("Use one explicit import package as alias.")
        self.package, self.alias = names[0].name, names[0].asname
        self.module = importlib.import_module(self.package)

    @property
    def source(self):
        return f"import {self.package} as {self.alias}"

    @property
    def namespace(self):
        return _ModuleView(self.module)


class _ModuleView:
    """Keep session import metadata separate from package attribute names."""

    def __init__(self, module):
        self._module = module

    def __getattr__(self, name):
        value = getattr(self._module, name)
        if inspect.isfunction(value) or inspect.isbuiltin(value):
            return value if self._module.__name__ == "math" else Function(value)
        return _ModuleView(value) if isinstance(value, ModuleType) else value
