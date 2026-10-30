from ato_foundation.models import (
    OperationRecord,
    Classification,
    Disposition,
    EvidenceRecord,
)
from ato_foundation.github.client import GitHubClient


class Verifier:
    def __init__(self, client: GitHubClient):
        self.client = client

    def verify(self, op: OperationRecord) -> OperationRecord:
        action = op.action
        target = action.get("target", "")

        try:
            if op.feature == "github.branch_protection":
                owner, repo_branch = target.split("/", 1)
                repo, branch = (repo_branch.split(":") + [""])[:2]
                actual = self.client.get_branch_protection(owner, repo, branch)
                op.observations.append({"actual_rules": actual})

                desired = action.get("desired_rules", {})
                matches = self._rules_match(actual, desired)

                if matches:
                    op.classification = Classification.VERIFIED
                    op.disposition = Disposition.SUCCESS
                else:
                    op.classification = Classification.REPORTED
                    op.disposition = Disposition.STOP
                    op.error = "Branch protection does not match desired state"

                evidence = EvidenceRecord.create(
                    classification=op.classification,
                    subject=op.operation_id,
                    observation={
                        "actual": actual,
                        "desired": desired,
                        "matches": matches,
                    },
                    parent_operation_id=op.operation_id,
                )
                op.evidence.append(evidence)

            elif op.feature == "github.collaborators":
                owner, repo = target.split("/", 1)
                actual = self.client.get_collaborators(owner, repo)
                op.observations.append({"actual_collaborators": actual})
                # Minimal placeholder comparison
                op.classification = Classification.REPORTED
                op.disposition = Disposition.SUCCESS
                evidence = EvidenceRecord.create(
                    classification=op.classification,
                    subject=op.operation_id,
                    observation={"actual_collaborators": actual},
                    parent_operation_id=op.operation_id,
                )
                op.evidence.append(evidence)

            else:
                op.classification = Classification.UNTESTED
                op.disposition = Disposition.INDETERMINATE
                op.error = f"No verifier implemented for feature {op.feature}"

        except Exception as e:
            op.classification = Classification.BLOCKED
            op.disposition = Disposition.BLOCKED
            op.error = str(e)

        return op

    def _rules_match(self, actual: dict, desired: dict) -> bool:
        """Compare actual branch protection against desired state.

        This is intentionally strict and expandable.
        """
        if not desired:
            return True  # nothing required

        # Example checks — expand as desired-state grows
        if desired.get("enforce_admins") is not None:
            if actual.get("enforce_admins") != desired["enforce_admins"]:
                return False

        if desired.get("required_pull_request_reviews"):
            if not actual.get("required_pull_request_reviews"):
                return False

        if desired.get("allow_force_pushes") is False:
            if actual.get("allow_force_pushes", True):
                return False

        return True
