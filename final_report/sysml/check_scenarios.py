#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = []
# ///
"""Semantic responsibility/style and guarded-link checks for ScenarioViews only."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import tomllib


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, required=True, help="path to the native model.py wrapper")
    parser.add_argument("--config", type=Path, help="override the scoped scenarios.toml for a check")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    config = args.config or root / "scenarios.toml"
    spec = importlib.util.spec_from_file_location("scenario_native_tool", args.tool.resolve())
    require(spec is not None and spec.loader is not None, "Cannot load the native model wrapper")
    tool = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tool
    spec.loader.exec_module(tool)

    # Use the same licensed checker and matching semantic API as native rendering.
    result = tool.validate([root], [], warnings_as_errors=True, config=config)
    model, api = tool.require_semantic_model(result)
    elements = list(model.nodes(api.Element, include_subtypes=True))
    compiler = api.Compiler()
    styles = tomllib.loads(config.read_text())["viz"]["style"]["group"]
    scenarios = [e for e in elements if type(e).__name__ == "ActionDefinition"
                 and str(e.owner.qualified_name) == "ScenarioViews"
                 and e.name.startswith("SC")]
    require(len(scenarios) == 3, "Expected three scenario action definitions")
    tasks = [e for e in elements if type(e).__name__ in ("ActionUsage", "PerformActionUsage")
             and e.owner in scenarios and e.declared_name]
    allocations = [e for e in elements if type(e).__name__ == "AllocationUsage"
                   and str(e.owner.qualified_name) == "ScenarioViews"]
    tags = {"ScenarioViews::FrameworkAction": ("ActionUsage", "framework"),
            "ScenarioViews::ExternalAction": ("PerformActionUsage", "external")}
    metadata = [e for e in elements if isinstance(e, api.MetadataUsage)
                and any(str(t.qualified_name) in tags for t in e.types)]

    def value(feature, scope):
        evaluated, report = compiler.evaluate_feature(feature, scope)
        require(bool(report), f"Cannot evaluate metadata feature {feature.name}")
        return evaluated

    for task in tasks:
        attached = [m for m in metadata if task in m.annotated_elements]
        require(len(attached) == 1, f"{task}: expected exactly one responsibility annotation")
        annotation = attached[0]
        tag = next(str(t.qualified_name) for t in annotation.types if str(t.qualified_name) in tags)
        kind, group_name = tags[tag]
        require(type(task).__name__ == kind, f"{task}: responsibility and native metaclass disagree")
        group = styles[group_name]
        require(group["members"] == [kind], f"{group_name}: wrong native style selector")
        fields = {f.name: f for f in annotation.owned_features}
        color = value(fields["fillColor"], annotation)
        require(color == group["fill_header"] == group["fill_body"], f"{task}: metadata/style color mismatch")
        performer = value(fields["performer"], annotation)
        require(isinstance(performer, api.BoundMetaclass), f"{task}: performer must reflect a modeled actor")
        actor = performer.element
        require(isinstance(actor, api.PartUsage), f"{task}: performer is not a modeled part")
        require((str(actor.qualified_name) == "ScenarioViews::framework") == (group_name == "framework"),
                f"{task}: framework/external performer mismatch")
        assigned = [a for a in allocations if a.source_feature == task]
        require(len(assigned) == 1 and list(assigned[0].target_features) == [actor],
                f"{task}: allocation does not match responsibility metadata")
        if group_name == "external":
            require(any(isinstance(t, api.ActionDefinition) and str(t.qualified_name).startswith("ScenarioViews::")
                        for t in task.types), f"{task}: external call lacks a named behavior definition")
    require(len(tasks) == len(metadata) == len(allocations) == 24, "Incomplete scenario responsibility coverage")

    transitions = [e for e in elements if type(e).__name__ == "TransitionUsage" and e.owner in scenarios]
    require(len(transitions) == 14, "Expected fourteen guarded alternative paths")
    for transition in transitions:
        links = [f for f in transition.owned_features if type(f).__name__ == "SuccessionAsUsage"]
        require(len(links) == 1, f"{transition}: expected one explicit guarded link")
        link = links[0]
        guard = " ".join(api.pprint(transition.guard_expression).split())
        require(link.name == f"[{guard}]", f"{transition}: printed guard label disagrees with modeled condition")
        require(link.source_feature == transition.source and list(link.target_features) == [transition.target],
                f"{transition}: printed link endpoints differ from conditional succession")
        lower, lower_report = compiler.evaluate(link.multiplicity.lower_bound)
        upper, upper_report = compiler.evaluate(link.multiplicity.upper_bound)
        require(bool(lower_report) and bool(upper_report) and (lower, upper) == (0, 1),
                f"{transition}: guarded link must remain optional [0..1]")
        bindings = [f for f in transition.owned_features if type(f).__name__ == "BindingConnectorAsUsage"
                    and f.source_feature == link]
        require(len(bindings) == 1, f"{transition}: explicit link is not bound to the controlled link")
        targets = list(bindings[0].target_features)
        require(len(targets) == 1 and targets[0].name == "transitionLink" and targets[0].owner == transition,
                f"{transition}: link binding does not preserve conditional-transition control")

    print("PASS: full model validation (zero warnings/errors); 24 ownership/color/actor allocations; 14 guarded links")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, AttributeError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
