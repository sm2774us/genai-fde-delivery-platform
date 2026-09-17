"""End-to-end CLI demo: ingestion -> RAG Q&A -> agentic tool-use -> HITL
approval -> eval harness report. Run with: python scripts/demo.py
"""
from app.agents.orchestrator import AgentOrchestrator
from app.core.logging import configure_logging

configure_logging()


def main():
    orch = AgentOrchestrator()
    orch.rag.ingest([
        {"doc_id": "kb-sso-1", "title": "SSO Migration Runbook",
         "text": "After the SSO migration, customers saw login failures due to stale session tokens. "
                 "Fix: clear session cache and reissue SAML assertions."},
    ])

    print("\n--- 1) Knowledge question (RAG path) ---")
    r1 = orch.run("Why are customers seeing login failures after the SSO migration?")
    print(r1.final_text)

    print("\n--- 2) Low-risk tool call (direct execution) ---")
    r2 = orch.run("lookup customer account information")
    print(r2.final_text)

    print("\n--- 3) High-risk action (HITL gate triggers) ---")
    r3 = orch.run("please escalate this case immediately")
    print(r3.final_text)

    print("\n--- 4) Human approves the pending action ---")
    orch.hitl.decide(r3.hitl_request_id, approve=True)
    r4 = orch.run("", approved_request_id=r3.hitl_request_id)
    print(r4.final_text)


if __name__ == "__main__":
    main()
