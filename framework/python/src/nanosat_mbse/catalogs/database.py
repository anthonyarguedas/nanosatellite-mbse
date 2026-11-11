"""Injectable product database access and database-backed object behavior."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Optional, Protocol, Tuple
from uuid import uuid4

from ..core.elements import Element
from ..core.requirements import Requirement, _parameter_name
from ..core.verification import PendingValue

FILES = (
    "products.tsv",
    "definitions.tsv",
    "parameters.tsv",
    "features.tsv",
    "conditions.tsv",
    "condition-parameters.tsv",
    "sources.tsv",
    "elements.tsv",
)
TYPES = {
    "Real": "float",
    "Integer": "integer",
    "Boolean": "boolean",
    "String": "string",
}


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    ).hexdigest()


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _plain(value):
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


@dataclass(frozen=True)
class Fact:
    id: str
    revision: str
    name: str
    element: str
    kind: str
    type: str
    unit: str
    value_kind: str
    value: object
    condition: Mapping
    source: Mapping

    def projection(self):
        return {
            "id": self.id,
            "revision": self.revision,
            "name": self.name,
            "element": self.element,
            "kind": self.kind,
            "type": self.type,
            "unit": self.unit,
            "valueKind": self.value_kind,
            "value": self.value,
            "condition": _plain(self.condition),
            "source": dict(self.source),
        }


@dataclass(frozen=True)
class ProductRecord:
    id: str
    model: str
    manufacturer: str
    part_number: str
    datasheet_url: str
    facts: Tuple[Fact, ...]
    pins: Tuple[Mapping, ...]
    record: Mapping

    def projection(self, include_pins=True):
        result = {
            "id": self.id,
            "name": f"{self.part_number} · {self.manufacturer}",
            "manufacturer": self.manufacturer,
            "partNumber": self.part_number,
            "model": self.model,
            "datasheetUrl": self.datasheet_url,
        }
        if include_pins:
            result["pins"] = [dict(pin) for pin in self.pins]
        return result


@dataclass(frozen=True)
class FactReference:
    key: str
    name: str
    fact: str
    revision: str
    type: str
    unit: str

    def __post_init__(self):
        _parameter_name(self.name)
        if self.type not in ("float", "integer", "boolean", "string"):
            raise ValueError("A COTS reference needs a supported scalar type.")
        if not self.key or not self.fact or not self.revision:
            raise ValueError("A COTS reference pins an identity and revision.")

    @classmethod
    def select(cls, name, fact, *, key=None):
        return cls(
            str(uuid4()) if key is None else key,
            name,
            fact.id,
            fact.revision,
            fact.type,
            fact.unit,
        )

    def projection(self):
        return {
            "key": self.key,
            "name": self.name,
            "fact": self.fact,
            "revision": self.revision,
            "type": self.type,
            "unit": self.unit,
        }


@dataclass(frozen=True)
class FactResolution:
    state: str
    value: object = None
    message: str = ""
    record: Optional[Fact] = None

    def projection(self):
        return {"state": self.state, "value": self.value, "message": self.message}


class ProductDatabase(Protocol):
    def products(self) -> Tuple[ProductRecord, ...]: ...
    def product(self, product_id: str) -> Optional[ProductRecord]: ...


def _scalar(text, kind):
    if kind == "string":
        return text
    if kind == "boolean":
        if text not in ("true", "false"):
            raise ValueError("Catalogue Boolean facts must be true or false.")
        return text == "true"
    value = float(text)
    if (
        not math.isfinite(value)
        or kind == "integer"
        and (not value.is_integer() or abs(value) > 9007199254740991)
    ):
        raise ValueError("Catalogue facts must contain finite, typed values.")
    return int(value) if kind == "integer" else value


@lru_cache(maxsize=4)
def _parse_catalog(sources, pin_source):
    tables = {
        name: list(csv.DictReader(io.StringIO(text), delimiter="\t"))
        for name, text in zip(FILES, sources)
    }
    products = {row["product_id"]: row for row in tables["products.tsv"]}
    if len(products) != len(tables["products.tsv"]) or any(
        not identity for identity in products
    ):
        raise ValueError("Product identities must be unique and nonempty.")
    definitions = {}
    for row in tables["definitions.tsv"]:
        key = (row["definition_kind"], row["name"])
        if key in definitions and definitions[key]["scalar_type"] != row["scalar_type"]:
            raise ValueError("Conflicting COTS fact types.")
        definitions[key] = row
    conditions = {row["condition_id"]: row for row in tables["conditions.tsv"]}
    condition_parameters = {}
    for row in tables["condition-parameters.tsv"]:
        condition_parameters.setdefault(row["condition_id"], []).append(row)
    provenance = {row["source_id"]: row for row in tables["sources.tsv"]}
    elements = {
        (row["product_id"], row["element_id"]): row for row in tables["elements.tsv"]
    }
    facts = {product: [] for product in products}
    identifiers = set()
    for kind, filename, column in (
        ("parameter", "parameters.tsv", "parameter_name"),
        ("feature", "features.tsv", "feature_name"),
    ):
        for row in tables[filename]:
            product, name, element = row["product_id"], row[column], row["element_id"]
            definition = definitions.get((kind, name))
            source = provenance.get(row["source_id"])
            condition_id = row.get("condition_id", "")
            condition = conditions.get(condition_id) if condition_id else None
            if (
                product not in products
                or definition is None
                or source is None
                or condition_id
                and condition is None
            ):
                raise ValueError(
                    "A COTS fact has an unresolved product, definition, source or condition."
                )
            value_type = TYPES[definition["scalar_type"]]
            identifier = digest(
                [
                    kind,
                    product,
                    element,
                    name,
                    row.get("value_kind", ""),
                    condition_id,
                    row["source_id"],
                    row["source_locator"],
                ]
            )
            if identifier in identifiers:
                raise ValueError("Ambiguous COTS fact identity.")
            identifiers.add(identifier)
            element_definition = elements.get(
                (product, element), {"element_id": element}
            )
            extra_conditions = []
            for item in condition_parameters.get(condition_id, []):
                condition_source = provenance.get(item["source_id"])
                if condition_source is None:
                    raise ValueError(
                        "An additional COTS condition has an unresolved source."
                    )
                extra_conditions.append(
                    {
                        **item,
                        "source_revision": condition_source["revision"],
                        "source_sha256": condition_source["sha256"],
                        "source_url": condition_source["url"],
                    }
                )
            revision = digest(
                [
                    row,
                    definition,
                    source,
                    condition,
                    extra_conditions,
                    element_definition,
                ]
            )
            facts[product].append(
                Fact(
                    identifier,
                    revision,
                    name,
                    element,
                    kind,
                    value_type,
                    row.get("unit", ""),
                    row.get("value_kind", "declared"),
                    _scalar(row["value"], value_type),
                    _freeze(
                        {
                            "id": condition_id,
                            "values": {
                                key: value
                                for key, value in (condition or {}).items()
                                if key != "condition_id" and value
                            },
                            "parameters": extra_conditions,
                        }
                    ),
                    MappingProxyType(
                        {
                            "id": row["source_id"],
                            "locator": row["source_locator"],
                            "url": source["url"],
                            "revision": source["revision"],
                            "sha256": source["sha256"],
                            "retrievedUtc": source["retrieved_utc"],
                        }
                    ),
                )
            )
    pins = list(csv.DictReader(io.StringIO(pin_source), delimiter="\t"))
    result = []
    for identifier, product in products.items():
        product_facts = tuple(
            sorted(
                facts[identifier],
                key=lambda fact: (
                    fact.element != "self",
                    fact.element,
                    fact.name,
                    fact.value_kind,
                    fact.condition["id"],
                    fact.id,
                ),
            )
        )
        product_pins = tuple(
            MappingProxyType(
                {
                    "number": pin["pin_number"],
                    "name": pin["pin_name"],
                    "kind": pin["pin_kind"],
                    "direction": pin["direction"],
                }
            )
            for pin in pins
            if pin["product_id"] == identifier and pin["element_id"] == "self"
        )
        result.append(
            ProductRecord(
                identifier,
                product["model_type"],
                product["manufacturer"],
                product["part_number"],
                product["datasheet_url"],
                product_facts,
                product_pins,
                MappingProxyType(dict(product)),
            )
        )
    return tuple(result)


class TabularDatabase:
    """Adapter for the existing TSV database, with content-keyed source caching."""

    def __init__(self, directory=None):
        configured = directory or os.environ.get("NANOSAT_MBSE_COTS_DIR")
        if configured is None:
            configured = next(
                (
                    parent / "cots"
                    for parent in Path(__file__).resolve().parents
                    if (parent / "cots" / "products.tsv").is_file()
                ),
                None,
            )
        self.directory = (
            None if configured is None else Path(configured).expanduser().resolve()
        )

    def products(self):
        if self.directory is None:
            raise FileNotFoundError(
                "Configure TabularDatabase(directory) or NANOSAT_MBSE_COTS_DIR for the COTS database."
            )
        try:
            sources = tuple(
                (self.directory / name).read_text(encoding="utf-8") for name in FILES
            )
            pin_source = (self.directory / "pins.tsv").read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Incomplete COTS database at {self.directory}. Configure a directory containing the framework COTS tables."
            ) from error
        return _parse_catalog(sources, pin_source)

    def product(self, product_id):
        return next(
            (product for product in self.products() if product.id == product_id), None
        )


class DatabaseBacked:
    """Cooperative mixin for component classes whose product facts live in a DB."""

    product_type = ""

    def __init__(
        self,
        *,
        product="",
        database=None,
        facts=(),
        requirement_links=(),
        usage=None,
        allow_unresolved=False,
        **kwargs,
    ):
        inherited = getattr(getattr(self, "owner", None), "session", None)
        self.database = database or (
            inherited.database if inherited is not None else TabularDatabase()
        )
        self._product = ""
        self._facts = ()
        self.requirement_links = tuple(requirement_links)
        self.usage = usage
        self._facts_present = bool(facts)
        self._set_product(product, allow_unresolved=allow_unresolved)
        self.facts = facts
        super().__init__(**kwargs)

    def _set_product(self, product, *, allow_unresolved=False):
        if not isinstance(product, str) or not product:
            raise ValueError("Choose a product identity from the database.")
        record = self.database.product(product)
        if not allow_unresolved and record is None:
            raise ValueError(f"Unknown COTS product {product!r}.")
        if (
            record is not None
            and self.product_type
            and record.model != self.product_type
        ):
            raise ValueError(
                f"{type(self).__name__} represents {self.product_type}, not {record.model}."
            )
        self._product = product

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, product):
        self._set_product(product)

    @property
    def product_record(self):
        return self.database.product(self.product)

    @property
    def usage(self):
        return self._usage

    @usage.setter
    def usage(self, value):
        if value is not None:
            if not isinstance(value, Element) or value.selection:
                raise TypeError("A COTS usage must be a physical Element instance.")
            if self.session is not None:
                self.session.get(value)
        self._usage = value
        if self.session is not None:
            self.session._model_state_present = True

    @property
    def requirement_links(self):
        return self._requirement_links

    @requirement_links.setter
    def requirement_links(self, requirements):
        unique = {}
        for requirement in requirements:
            if not isinstance(requirement, Requirement):
                raise TypeError(
                    "COTS requirement links must reference Requirement instances."
                )
            if requirement.key in unique and unique[requirement.key] is not requirement:
                raise ValueError("Distinct linked requirements cannot share a key.")
            if self.session is not None:
                self.session.get(requirement)
            unique[requirement.key] = requirement
        self._requirement_links = tuple(unique.values())

    @property
    def facts(self):
        return self._facts

    @facts.setter
    def facts(self, references):
        references = tuple(references)
        if any(not isinstance(reference, FactReference) for reference in references):
            raise TypeError("COTS selections must be FactReference objects.")
        if len({reference.name for reference in references}) != len(references) or len(
            {reference.key for reference in references}
        ) != len(references):
            raise ValueError("COTS reference names and keys must be unique.")
        self._facts = references

    def suggested_reference_name(self, fact):
        names = {reference.name for reference in self.facts}
        base = fact.name[:35]
        candidates = (base, f"{base[:28]}_{fact.value_kind[:10]}")
        for candidate in (
            *candidates,
            *(f"{base}_{index}" for index in range(2, 1000)),
        ):
            try:
                _parameter_name(candidate)
            except ValueError:
                continue
            if candidate not in names:
                return candidate
        raise ValueError("Choose a unique name for this COTS reference.")

    def select_fact(self, name, fact, *, key=None):
        record = self.product_record
        if isinstance(fact, str):
            fact = (
                next((item for item in record.facts if item.id == fact), None)
                if record
                else None
            )
        if (
            fact is None
            or record is None
            or not any(item.id == fact.id for item in record.facts)
        ):
            raise ValueError("Select a fact from this component's product.")
        reference = FactReference.select(name, fact, key=key)
        self.facts = tuple(item for item in self.facts if item.name != name) + (
            reference,
        )
        self._facts_present = True
        return reference

    def resolve_reference(self, reference):
        record = self.product_record
        fact = (
            next((fact for fact in record.facts if fact.id == reference.fact), None)
            if record
            else None
        )
        if fact is None:
            return FactResolution(
                "pending",
                message="The selected record is unavailable for this product. Rebind it in the COTS pane.",
            )
        if (
            fact.revision != reference.revision
            or fact.type != reference.type
            or fact.unit != reference.unit
        ):
            return FactResolution(
                "pending",
                message="The catalogue record changed. Review and update its reference in the COTS pane.",
                record=fact,
            )
        return FactResolution("value", fact.value, record=fact)

    def assess(self, assessments):
        """Aggregate affected requirement results without executing an analysis."""
        from ..core.predicates import (
            MethodResult,
            VerificationResult,
            VerificationState,
        )

        methods = []
        for requirement in self.requirement_links:
            result = assessments.get(requirement, assessments.get(requirement.key))
            if isinstance(result, dict):
                state = VerificationState(result["state"])
                message = result.get("message", "")
            elif result is not None:
                state = result.state
                message = "\n".join(method.message for method in result.methods)
            else:
                state, message = (
                    VerificationState.PENDING,
                    "Evaluate the affected requirement.",
                )
            methods.append(MethodResult(requirement.id, state, message))
        return VerificationResult(tuple(methods))

    def verify(self, **kwargs):
        """Use the owning session's common verification context and current evidence."""
        if self.session is None:
            raise ValueError(
                "Attach the COTS component before verifying its requirements."
            )
        return self.assess(self.session.verify(**kwargs))

    def fact_value(self, name):
        reference = next(
            (reference for reference in self.facts if reference.name == name), None
        )
        if reference is None:
            raise KeyError(f"Unknown COTS reference {self.id}.{name}.")
        result = self.resolve_reference(reference)
        if result.state != "value":
            raise PendingValue(result.message)
        return result.value
