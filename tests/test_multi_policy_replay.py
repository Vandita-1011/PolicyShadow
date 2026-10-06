"""Connectivity check: real dataset -> two real policies -> combined real violations."""

from policyshadow.data.multi_policy_replay import replay_all_policies


def test_multi_policy_replay_produces_two_violation_types(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))

    rule_names = {v.rule_name for v in violations}
    assert "restrict-privileged-containers" in rule_names
    assert "require-non-root" in rule_names
    assert len(violations) > 15
