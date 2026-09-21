"""Fixed synthetic AdmissionReview-style records for Milestone 1 regression testing."""

from policyshadow.core.schemas import AdmissionReviewRecord, Operation


def _pod(name, namespace, containers, init_containers=None):
    spec = {"containers": containers}
    if init_containers:
        spec["initContainers"] = init_containers
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
    }


def _container(name, image, privileged=None, run_as_non_root=None):
    c = {"name": name, "image": image}
    sc = {}
    if privileged is not None:
        sc["privileged"] = privileged
    if run_as_non_root is not None:
        sc["runAsNonRoot"] = run_as_non_root
    if sc:
        c["securityContext"] = sc
    return c


SYNTHETIC_RECORDS = [
    AdmissionReviewRecord(
        record_id="r01", operation=Operation.CREATE, namespace="default",
        resource_kind="Pod", resource_name="web-app",
        resource_manifest=_pod("web-app", "default", [_container("app", "nginx:1.25", run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r02", operation=Operation.CREATE, namespace="default",
        resource_kind="Pod", resource_name="debug-app",
        resource_manifest=_pod("debug-app", "default", [_container("app", "nginx:1.25", privileged=True, run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r03", operation=Operation.CREATE, namespace="web",
        resource_kind="Pod", resource_name="frontend",
        resource_manifest=_pod("frontend", "web", [_container("app", "node:20", privileged=False, run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r04", operation=Operation.CREATE, namespace="web",
        resource_kind="Pod", resource_name="frontend-multi",
        resource_manifest=_pod(
            "frontend-multi", "web",
            [_container("app", "node:20", privileged=False), _container("sidecar", "envoy:1.28", privileged=True)],
        ),
    ),
    AdmissionReviewRecord(
        record_id="r05", operation=Operation.CREATE, namespace="payments",
        resource_kind="Pod", resource_name="payments-api",
        resource_manifest=_pod("payments-api", "payments", [_container("app", "payments:2.1", run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r06", operation=Operation.CREATE, namespace="payments",
        resource_kind="Pod", resource_name="payments-debug",
        resource_manifest=_pod("payments-debug", "payments", [_container("app", "payments:2.1", privileged=True, run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r07", operation=Operation.CREATE, namespace="batch",
        resource_kind="Pod", resource_name="etl-job",
        resource_manifest=_pod(
            "etl-job", "batch",
            [_container("app", "etl:1.0")],
            init_containers=[_container("init-setup", "busybox:1.36", privileged=False)],
        ),
    ),
    AdmissionReviewRecord(
        record_id="r08", operation=Operation.CREATE, namespace="batch",
        resource_kind="Pod", resource_name="etl-job-privileged-init",
        resource_manifest=_pod(
            "etl-job-privileged-init", "batch",
            [_container("app", "etl:1.0")],
            init_containers=[_container("init-setup", "busybox:1.36", privileged=True)],
        ),
    ),
    AdmissionReviewRecord(
        record_id="r09", operation=Operation.CREATE, namespace="monitoring",
        resource_kind="Pod", resource_name="prometheus",
        resource_manifest=_pod("prometheus", "monitoring", [_container("app", "prometheus:2.53")]),
    ),
    AdmissionReviewRecord(
        record_id="r10", operation=Operation.CREATE, namespace="monitoring",
        resource_kind="Pod", resource_name="debug-tools",
        resource_manifest=_pod("debug-tools", "monitoring", [_container("app", "debug-tools:latest", privileged=True, run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r11", operation=Operation.UPDATE, namespace="default",
        resource_kind="Pod", resource_name="redis",
        resource_manifest=_pod("redis", "default", [_container("app", "redis:7.2")]),
    ),
    AdmissionReviewRecord(
        record_id="r12", operation=Operation.UPDATE, namespace="default",
        resource_kind="Pod", resource_name="redis-debug",
        resource_manifest=_pod("redis-debug", "default", [_container("app", "redis:7.2", privileged=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r13", operation=Operation.CREATE, namespace="logging",
        resource_kind="Pod", resource_name="fluentd",
        resource_manifest=_pod("fluentd", "logging", [_container("app", "fluentd:1.16", privileged=False, run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r14", operation=Operation.CREATE, namespace="logging",
        resource_kind="Pod", resource_name="fluentd-debug",
        resource_manifest=_pod("fluentd-debug", "logging", [_container("app", "fluentd:1.16", privileged=True, run_as_non_root=True)]),
    ),
    AdmissionReviewRecord(
        record_id="r15", operation=Operation.CREATE, namespace="cache",
        resource_kind="Pod", resource_name="memcached",
        resource_manifest=_pod("memcached", "cache", [_container("app", "memcached:1.6")]),
    ),
    AdmissionReviewRecord(
        record_id="r16", operation=Operation.CREATE, namespace="cache",
        resource_kind="Pod", resource_name="memcached-privileged",
        resource_manifest=_pod("memcached-privileged", "cache", [_container("app", "memcached:1.6", privileged=True)]),
    ),
]
