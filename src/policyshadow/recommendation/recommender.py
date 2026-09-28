"""Generates a phased rollout recommendation for a cluster. NOT a risk score."""

from policyshadow.explanation.explainer import MODEL, TEMPERATURE, _get_client

CATEGORIES = [
    "Proceed toward Enforce",
    "Continue Audit while remediation occurs",
    "Modify the policy",
    "Delay enforcement",
    "Perform further assessment",
]

ENFORCE = "Proceed toward Enforce"
MAX_ATTEMPTS = 2


def assess_risk_level(affected_count: int, total_count: int) -> str:
    ratio = affected_count / total_count
    if ratio < 0.20:
        return "Low"
    if ratio <= 0.60:
        return "Medium"
    return "High"


def allowed_categories(risk_level: str) -> list[str]:
    if risk_level == "Low":
        return CATEGORIES
    return [c for c in CATEGORIES if c != ENFORCE]


def _build_prompt(
    cluster: dict, explanation: str, total_records: int, risk_level: str, allowed: list[str]
) -> str:
    category_list = "\n".join(f"- {c}" for c in allowed)
    return f"""You are recommending a rollout step for a Kubernetes admission policy,
based on historical replay evidence. This is a RECOMMENDATION for a human
platform engineer to review and approve or reject — it is not an automatic
decision, and you must not claim otherwise.

Rule: {cluster['rule_name']}
Affected workloads: {cluster['violation_count']} out of {total_records} historical records evaluated
Risk level (computed from the affected share, not your judgment): {risk_level}

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
explanation above, consistent with the risk level above, and explicitly
noting this requires engineer approval>"""


def _correction(category: str, risk_level: str, allowed: list[str]) -> str:
    options = "\n".join(f"- {c}" for c in allowed)
    return (
        f"The category {category!r} is not permitted for a {risk_level} risk level. "
        f"Choose exactly one from this list, copied exactly:\n{options}\n"
        "Respond again in the same format (CATEGORY: ... then RATIONALE: ...)."
    )


def recommend_rollout(cluster: dict, explanation: str, total_records: int) -> dict:
    risk_level = assess_risk_level(cluster["violation_count"], total_records)
    allowed = allowed_categories(risk_level)
    messages = [{
        "role": "user",
        "content": _build_prompt(cluster, explanation, total_records, risk_level, allowed),
    }]

    for _ in range(MAX_ATTEMPTS):
        text = _get_client().chat.completions.create(
            model=MODEL, messages=messages, temperature=TEMPERATURE
        ).choices[0].message.content
        category_line = next(
            (l for l in text.strip().split("\n") if l.startswith("CATEGORY:")), ""
        )
        category = category_line.replace("CATEGORY:", "").strip()
        if category in allowed:
            rationale = text.split("RATIONALE:", 1)[-1].strip() if "RATIONALE:" in text else text
            return {
                "category": category,
                "risk_level": risk_level,
                "rationale": rationale,
                "raw_text": text,
            }
        messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": _correction(category, risk_level, allowed)})

    raise ValueError(
        f"LLM returned a category not permitted for risk level {risk_level}: {category!r}"
    )
