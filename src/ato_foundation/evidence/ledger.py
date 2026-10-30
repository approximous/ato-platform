from pathlib import Path
import json
from typing import List, Union

from ato_foundation.models import EvidenceRecord, OperationRecord


class EvidenceLedger:
    """Append-only, content-addressed evidence store."""

    def __init__(self, path: str = "evidence/ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: Union[EvidenceRecord, OperationRecord]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            if isinstance(record, EvidenceRecord):
                f.write(json.dumps(record.__dict__, default=str) + "\n")
            else:
                f.write(json.dumps(record.to_dict(), default=str) + "\n")

    def load(self) -> List[dict]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
