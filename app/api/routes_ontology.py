from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.agents.hitl import get_hitl_queue
from app.api.schemas import ActionInvokeRequest, ApprovalDecision
from app.ontology.registry import get_registry

router = APIRouter(tags=["ontology"])


@router.get("/ontology/objects/{object_type}")
def list_objects(object_type: str):
    reg = get_registry()
    if object_type not in reg.object_types:
        raise HTTPException(404, f"unknown object type '{object_type}'")
    return {"object_type": object_type, "objects": reg.list_objects(object_type)}


@router.get("/ontology/schema")
def get_schema():
    reg = get_registry()
    return {
        "object_types": {k: [p.name for p in v.properties] for k, v in reg.object_types.items()},
        "action_types": {k: {"risk": v.risk.value, "requires_approval": v.requires_approval} for k, v in reg.action_types.items()},
        "link_types": {k: {"source": v.source_object, "target": v.target_object} for k, v in reg.link_types.items()},
    }


@router.post("/actions/invoke")
def invoke_action(req: ActionInvokeRequest):
    reg = get_registry()
    if req.action_api_name not in reg.action_types:
        raise HTTPException(404, f"unknown action '{req.action_api_name}'")
    return reg.invoke_action(req.action_api_name, req.payload, req.actor, req.approved)


@router.get("/hitl/pending")
def hitl_pending():
    q = get_hitl_queue()
    return {"pending": [r.__dict__ for r in q.pending()]}


@router.post("/hitl/decide")
def hitl_decide(decision: ApprovalDecision):
    q = get_hitl_queue()
    req = q.decide(decision.request_id, decision.approve)
    return req.__dict__
