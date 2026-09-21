"""Combined dataset: original hand-written records plus loaded manifest files."""

from pathlib import Path

from policyshadow.data.manifest_loader import load_manifests
from policyshadow.data.synthetic_records import SYNTHETIC_RECORDS

MANIFESTS_DIR = str(Path(__file__).parent / "manifests")

ALL_RECORDS = SYNTHETIC_RECORDS + load_manifests(MANIFESTS_DIR)
