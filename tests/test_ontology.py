from app.ontology.registry import OntologyRegistry


def test_seeded_customer_exists():
    reg = OntologyRegistry()
    customer = reg.get_object("Customer", "C-100")
    assert customer is not None
    assert customer["name"] == "Acme Corp"


def test_high_risk_action_requires_approval():
    reg = OntologyRegistry()
    result = reg.invoke_action("escalate_case", {"case_id": "CS-1"}, actor="tester", approved=False)
    assert result["status"] == "pending_approval"


def test_high_risk_action_executes_when_approved():
    reg = OntologyRegistry()
    result = reg.invoke_action("escalate_case", {"case_id": "CS-1"}, actor="tester", approved=True)
    assert result["status"] == "executed"
    assert result["result"]["new_status"] == "escalated"


def test_object_validation_rejects_missing_required_field():
    reg = OntologyRegistry()
    errors = reg.put_object("Customer", {"name": "No ID Corp"})
    assert errors
