"""Ontology registry + a sample "Client Operations" domain model: Case, Customer,
Document, and a governed `escalate_case` write-back action requiring HITL
approval when risk is high — mirroring an AIP action pattern."""
from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.ontology.models import (
    ActionAudit,
    ActionRisk,
    ActionType,
    LinkType,
    ObjectType,
    Property,
    PropertyType,
)

log = get_logger(__name__)


def _handle_escalate_case(payload: dict[str, Any]) -> dict[str, Any]:
    return {"case_id": payload["case_id"], "new_status": "escalated", "assigned_to": "tier2-queue"}


def _handle_update_customer_risk(payload: dict[str, Any]) -> dict[str, Any]:
    return {"customer_id": payload["customer_id"], "risk_score": payload["risk_score"]}


class OntologyRegistry:
    def __init__(self) -> None:
        self.object_types: dict[str, ObjectType] = {}
        self.link_types: dict[str, LinkType] = {}
        self.action_types: dict[str, ActionType] = {}
        self.audit_log: list[ActionAudit] = []
        self._object_store: dict[str, dict[str, dict[str, Any]]] = {}
        self._seed_domain()

    # -- registration -------------------------------------------------
    def register_object_type(self, ot: ObjectType) -> None:
        self.object_types[ot.api_name] = ot
        self._object_store.setdefault(ot.api_name, {})

    def register_link_type(self, lt: LinkType) -> None:
        self.link_types[lt.api_name] = lt

    def register_action_type(self, at: ActionType) -> None:
        self.action_types[at.api_name] = at

    # -- data ops -------------------------------------------------------
    def put_object(self, object_type: str, instance: dict[str, Any]) -> list[str]:
        ot = self.object_types[object_type]
        errors = ot.validate(instance)
        if errors:
            return errors
        self._object_store[object_type][instance[ot.primary_key]] = instance
        return []

    def get_object(self, object_type: str, key: str) -> dict[str, Any] | None:
        return self._object_store.get(object_type, {}).get(key)

    def list_objects(self, object_type: str) -> list[dict[str, Any]]:
        return list(self._object_store.get(object_type, {}).values())

    # -- governed actions -------------------------------------------------
    def invoke_action(
        self, action_api_name: str, payload: dict[str, Any], actor: str, approved: bool = False
    ) -> dict[str, Any]:
        action = self.action_types[action_api_name]
        if action.requires_approval and not approved:
            audit = ActionAudit(action_api_name, actor, payload, approved=False, result={})
            self.audit_log.append(audit)
            return {"status": "pending_approval", "risk": action.risk.value, "action": action_api_name}
        result = action.handler(payload)
        audit = ActionAudit(action_api_name, actor, payload, approved=True, result=result)
        self.audit_log.append(audit)
        log.info("ontology_action_invoked", action=action_api_name, actor=actor, risk=action.risk.value)
        return {"status": "executed", "result": result}

    # -- seed a demo domain -------------------------------------------------
    def _seed_domain(self) -> None:
        self.register_object_type(ObjectType(
            api_name="Customer", display_name="Customer",
            primary_key="customer_id",
            properties=[
                Property("customer_id", PropertyType.STRING, required=True),
                Property("name", PropertyType.STRING, required=True),
                Property("risk_score", PropertyType.NUMBER),
                Property("tier", PropertyType.STRING),
            ],
        ))
        self.register_object_type(ObjectType(
            api_name="Case", display_name="Support Case",
            primary_key="case_id",
            properties=[
                Property("case_id", PropertyType.STRING, required=True),
                Property("customer_id", PropertyType.STRING, required=True),
                Property("status", PropertyType.STRING, required=True),
                Property("summary", PropertyType.STRING),
            ],
        ))
        self.register_object_type(ObjectType(
            api_name="Document", display_name="Knowledge Document",
            primary_key="doc_id",
            properties=[
                Property("doc_id", PropertyType.STRING, required=True),
                Property("title", PropertyType.STRING, required=True),
                Property("source", PropertyType.STRING),
            ],
        ))
        self.register_link_type(LinkType("customer_cases", "Customer", "Case", "one-to-many"))
        self.register_action_type(ActionType(
            api_name="escalate_case", display_name="Escalate Case",
            target_object="Case", risk=ActionRisk.HIGH,
            handler=_handle_escalate_case, requires_approval=True,
        ))
        self.register_action_type(ActionType(
            api_name="update_customer_risk", display_name="Update Customer Risk Score",
            target_object="Customer", risk=ActionRisk.MEDIUM,
            handler=_handle_update_customer_risk, requires_approval=False,
        ))
        # seed a few rows so the demo has data end-to-end
        self.put_object("Customer", {"customer_id": "C-100", "name": "Acme Corp", "risk_score": 0.2, "tier": "gold"})
        self.put_object("Case", {"case_id": "CS-1", "customer_id": "C-100", "status": "open",
                                  "summary": "Customer reports repeated login failures after SSO migration."})


_registry_singleton: OntologyRegistry | None = None


def get_registry() -> OntologyRegistry:
    global _registry_singleton
    if _registry_singleton is None:
        _registry_singleton = OntologyRegistry()
    return _registry_singleton
