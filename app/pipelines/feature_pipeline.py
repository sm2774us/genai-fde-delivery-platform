"""Feature-engineering pipeline stub over the ontology's Customer objects —
demonstrates the "data pipelines powering GenAI use cases" and
"feature engineering / model evaluation" preferred qualifications with a
Spark-style transform interface (pure functions over record batches) that
would port directly onto PySpark DataFrames in a real deployment."""
from __future__ import annotations

from app.ontology.registry import get_registry


def compute_customer_risk_features(customers: list[dict]) -> list[dict]:
    """Pure transform: derive simple engineered features per customer. In
    production this would be a PySpark job reading/writing to the lakehouse;
    kept in-memory here for portability."""
    features = []
    for c in customers:
        tier_weight = {"gold": 0.5, "silver": 0.75, "bronze": 1.0}.get(c.get("tier", "bronze"), 1.0)
        base_risk = c.get("risk_score", 0.5)
        features.append({
            "customer_id": c["customer_id"],
            "adjusted_risk_score": round(base_risk * tier_weight, 4),
            "tier_weight": tier_weight,
        })
    return features


def run_feature_pipeline() -> list[dict]:
    reg = get_registry()
    customers = reg.list_objects("Customer")
    return compute_customer_risk_features(customers)
