"""Foundry/AIP-style semantic layer: Object Types, Link Types, Action Types.

Palantir's core differentiator is modeling the client's business as an
Ontology (objects + relationships + governed write-back actions) rather than
raw tables. This module reproduces that pattern in a lightweight, portable
way so the concept is demonstrable without the real platform.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class PropertyType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"


@dataclass
class Property:
    name: str
    type: PropertyType
    required: bool = False


@dataclass
class ObjectType:
    """Analogous to a Foundry Object Type: a governed business entity."""
    api_name: str
    display_name: str
    properties: list[Property]
    primary_key: str

    def validate(self, instance: dict[str, Any]) -> list[str]:
        errors = []
        for prop in self.properties:
            if prop.required and prop.name not in instance:
                errors.append(f"missing required property '{prop.name}'")
        if self.primary_key not in instance:
            errors.append(f"missing primary key '{self.primary_key}'")
        return errors


@dataclass
class LinkType:
    """Analogous to a Foundry Link Type: a typed relationship between objects."""
    api_name: str
    source_object: str
    target_object: str
    cardinality: str = "many-to-many"  # one-to-one | one-to-many | many-to-many


class ActionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ActionType:
    """Analogous to a Foundry Action Type / AIP write-back action: a governed,
    auditable mutation with an optional human-in-the-loop approval gate."""
    api_name: str
    display_name: str
    target_object: str
    risk: ActionRisk
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    requires_approval: bool = False


@dataclass
class ActionAudit:
    action_api_name: str
    actor: str
    payload: dict[str, Any]
    approved: bool
    result: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
