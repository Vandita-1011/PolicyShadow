"""Generates grounded explanations for a violation cluster using Groq."""

import os
import re

from groq import Groq

MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def _build_prompt(cluster: dict) -> str:
    evidence_text = "\n\n".join(
        f"[{e['source']}]\n{e['text']}" for e in cluster["evidence"]
    )
    return f"""You are explaining a Kubernetes admission policy violation to a platform engineer.

Rule violated: {cluster['rule_name']}
Number of affected workloads: {cluster['violation_count']}

Reference evidence (use ONLY this evidence, cite the source filename
using plain square brackets like [filename.txt] for every factual
claim — always use standard ASCII brackets, never any other bracket
style — do not use outside knowledge):

{evidence_text}

Write:
1. A short explanation of what this rule violation means and why it matters.
2. Remediation guidance, grounded only in the evidence above.

If the evidence does not fully support a claim, say so explicitly rather
than inventing information."""


def _normalize_citations(text: str) -> str:
    text = text.replace("【", "[").replace("】", "]")
    return re.sub(r"\[\s*([^\[\]]+?)\s*\]", r"[\1]", text)


def explain_cluster(cluster: dict) -> str:
    response = _get_client().chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": _build_prompt(cluster)}],
    )
    return _normalize_citations(response.choices[0].message.content)

