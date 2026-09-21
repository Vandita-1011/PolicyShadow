"""JSON file-based violation storage for Milestone 1."""

import json
from pathlib import Path

from policyshadow.core.interfaces import ViolationRepository
from policyshadow.core.schemas import Violation


class JSONFileViolationRepository(ViolationRepository):
    def __init__(self, path: str):
        self.path = Path(path)

    def save(self, violations: list[Violation]) -> None:
        self.path.write_text(json.dumps([v.model_dump(mode="json") for v in violations], indent=2))

    def get_all(self) -> list[Violation]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text())
        return [Violation(**v) for v in data]
