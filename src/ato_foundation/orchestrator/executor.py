from ato_foundation.models import (
    OperationRecord,
    Mode,
    Disposition,
    Classification,
)
from ato_foundation.github.client import GitHubClient
from ato_foundation.orchestrator.verifier import Verifier
from ato_foundation.evidence.ledger import EvidenceLedger


class Executor:
    def __init__(
        self, client: GitHubClient, verifier: Verifier, ledger: EvidenceLedger
    ):
        self.client = client
        self.verifier = verifier
        self.ledger = ledger

    def run(self, op: OperationRecord) -> OperationRecord:
        # 1. Authorization gate
        if op.authorization.required and op.authorization.status != "GRANTED":
            op.disposition = Disposition.REQUIRE_HUMAN
            op.classification = Classification.BLOCKED
            self.ledger.append(op)
            return op

        # 2. Mode handling
        if op.mode == Mode.PLAN:
            op.disposition = Disposition.SUCCESS
            op.classification = Classification.INFERRED
            self.ledger.append(op)
            return op

        if op.mode in (Mode.VERIFY, Mode.ASSURE):
            result = self.verifier.verify(op)
            self.ledger.append(result)
            return result

        if op.mode == Mode.APPLY:
            # Perform the authorized write
            if op.feature == "github.branch_protection":
                target = op.action["target"]
                owner, repo_branch = target.split("/", 1)
                repo, branch = repo_branch.split(":")
                rules = op.action.get("desired_rules", {})
                self.client.update_branch_protection(owner, repo, branch, rules)

            # Always re-verify after any write
            result = self.verifier.verify(op)
            self.ledger.append(result)
            return result

        op.disposition = Disposition.BLOCKED
        op.error = f"Unsupported mode {op.mode}"
        self.ledger.append(op)
        return op
