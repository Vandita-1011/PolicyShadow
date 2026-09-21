"""Groups violations by semantic similarity of their embeddings."""

from sklearn.cluster import AgglomerativeClustering

from policyshadow.core.schemas import Violation

DISTANCE_THRESHOLD = 0.1


def cluster_violations(
    violations: list[Violation], embeddings: dict[str, list[float]]
) -> dict[str, list[str]]:
    ids = [v.violation_id for v in violations]
    vectors = [embeddings[vid] for vid in ids]

    model = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=DISTANCE_THRESHOLD,
        metric="cosine",
        linkage="average",
    )
    labels = model.fit_predict(vectors)

    clusters: dict[str, list[str]] = {}
    for vid, label in zip(ids, labels):
        clusters.setdefault(f"cluster-{label}", []).append(vid)
    return clusters
