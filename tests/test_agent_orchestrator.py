from app.agents.orchestrator import AgentOrchestrator


def test_high_risk_tool_triggers_hitl_gate():
    orch = AgentOrchestrator()
    result = orch.run("please escalate this case immediately")
    assert result.hitl_request_id is not None
    assert any(s.kind == "hitl_pending" for s in result.steps)


def test_approved_hitl_request_executes_action():
    orch = AgentOrchestrator()
    result = orch.run("please escalate this case immediately")
    request_id = result.hitl_request_id
    orch.hitl.decide(request_id, approve=True)
    final = orch.run("", approved_request_id=request_id)
    assert "executed" in final.final_text.lower()


def test_low_risk_lookup_executes_directly():
    orch = AgentOrchestrator()
    result = orch.run("lookup customer account information")
    assert result.hitl_request_id is None


def test_falls_back_to_rag_for_knowledge_question():
    orch = AgentOrchestrator()
    result = orch.run("what happened during the SSO migration")
    assert any(s.kind == "rag_answer" for s in result.steps)
