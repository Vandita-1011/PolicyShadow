"""Generates a phased rollout recommendation for a cluster. NOT a risk score."""

from policyshadow.explanation.explainer import _get_client, MODEL

CATEGORIES = [
    "Proceed toward Enforce",
    "Continue Audit while remediation occurs",
    "Modify the policy",
    "Delay enforcement",
    "Perform further assessment",
]


def assess_risk_level(affected_count: int, total_count: int) -> str:
    ratio = affected_count / total_count
    if ratio < 0.20:
        return "Low"
    if ratio <= 0.60:
        return "Medium"
    return "High"


def _build_prompt(cluster: dict, explanation: str, total_records: int) -> str:
    category_list = "\n".join(f"- {c}" for c in CATEGORIES)
    return f"""You are recommending a rollout step for a Kubernetes admission policy,
based on historical replay evidence. This is a RECOMMENDATION for a human
platform engineer to review and approve or reject — it is not an automatic
decision, and you must not claim otherwise.

Rule: {cluster['rule_name']}
Affected workloads: {cluster['violation_count']} out of {total_records} historical records evaluated

Grounded explanation of this violation cluster:
{explanation}

Choose EXACTLY ONE category from this fixed list (copy it exactly,
character for character, do not invent a new category or modify the
wording):
{category_list}

Do NOT produce a numeric score of any kind.

Respond in exactly this format:
CATEGORY: <one of the categories above, copied exactly>
RATIONALE: <2-3 sentences explaining why, grounded in the numbers and
explanation above, and explicitly noting this requires engineer approval>"""


def recommend_rollout(cluster: dict, explanation: str, total_records: int) -> dict:
    prompt = _build_prompt(cluster, explanation, total_records)
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content

    lines = text.strip().split("\n")
    category_line = next((l for l in lines if l.startswith("CATEGORY:")), "")
    category = category_line.replace("CATEGORY:", "").strip()
    rationale = text.split("RATIONALE:", 1)[-1].strip() if "RATIONALE:" in text else text

    if category not in CATEGORIES:
        raise ValueError(f"LLM returned an invalid category: {category!r}")

    risk_level = assess_risk_level(cluster["violation_count"], total_records)
    return {
        "category": category,
        "risk_level": risk_level,
        "rationale": rationale,
        "raw_text": text,
    }
