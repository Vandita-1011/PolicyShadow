"""Deterministic + real-Kyverno tests for policy validation."""

from policyshadow.policy_engines.policy_validator import validate_policy_yaml

VALID_POLICY = """
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-team-label
spec:
  background: true
  rules:
    - name: require-team-label
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        failureAction: Audit
        message: "Pods must have a team label."
        pattern:
          metadata:
            labels:
              team: "?*"
"""


def test_empty_policy_rejected():
    valid, error = validate_policy_yaml("")
    assert not valid
    assert "empty" in error.lower()


def test_malformed_yaml_rejected():
    valid, error = validate_policy_yaml("not: valid: yaml: [structure")
    assert not valid
    assert "yaml" in error.lower()


def test_wrong_api_version_rejected():
    valid, error = validate_policy_yaml("apiVersion: v1\nkind: Pod\nmetadata:\n  name: x")
    assert not valid
    assert "apiVersion" in error


def test_missing_rules_rejected():
    valid, error = validate_policy_yaml(
        "apiVersion: kyverno.io/v1\nkind: ClusterPolicy\nmetadata:\n  name: x\nspec: {}"
    )
    assert not valid
    assert "rules" in error.lower()


def test_valid_kyverno_policy_accepted():
    valid, error = validate_policy_yaml(VALID_POLICY)
    assert valid, error
    assert error is None
