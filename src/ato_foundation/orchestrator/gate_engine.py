from typing import List, Dict

from ato_foundation.models import OperationRecord, Disposition, Classification


GATES = {
    "G1": ["ATO-GH-BOOTSTRAP-001.G1."],
    "G2": ["ATO-GH-BOOTSTRAP-001.G2."],
    "G3": ["ATO-GH-BOOTSTRAP-001.G3."],
    "G4": ["ATO-GH-BOOTSTRAP-001.G4."],
    "G5": ["ATO-GH-BOOTSTRAP-001.G5."],
}


class GateEngine:
    def evaluate(self, records: List[OperationRecord]) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for gate, prefixes in GATES.items():
            gate_ops = [
                r
                for r in records
                if any(r.operation_id.startswith(p) for p in prefixes)
            ]
            if not gate_ops:
                results[gate] = "UNTESTED"
                continue
            if any(r.disposition == Disposition.BLOCKED for r in gate_ops):
                results[gate] = "BLOCKED"
            elif any(
                r.classification in (Classification.BLOCKED, Classification.UNTESTED)
                for r in gate_ops
            ):
                results[gate] = "CONDITIONAL"
            elif all(r.disposition == Disposition.SUCCESS for r in gate_ops):
                results[gate] = "QUALIFIED"
            else:
                results[gate] = "INDETERMINATE"
        return results
