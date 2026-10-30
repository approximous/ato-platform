from typing import List
import yaml

from ato_foundation.models import (
    OperationRecord,
    Mode,
    Authorization,
)


class Planner:
    def __init__(self, desired_state_path: str):
        with open(desired_state_path, encoding="utf-8") as f:
            self.desired = yaml.safe_load(f)

    def plan_github_bootstrap(self, mode: Mode = Mode.VERIFY) -> List[OperationRecord]:
        ops: List[OperationRecord] = []
        rev = str(self.desired.get("revision", "0.0.0"))
        owner = self.desired["repository"]["owner"]
        repo = self.desired["repository"]["name"]
        branch = self.desired["repository"].get("default_branch", "main")

        # G2 — Branch protection
        ops.append(
            OperationRecord(
                operation_id="ATO-GH-BOOTSTRAP-001.G2.BRANCH-RULES",
                feature="github.branch_protection",
                mode=mode,
                desired_state_revision=rev,
                preconditions=[
                    {"type": "repo_exists", "owner": owner, "repo": repo},
                    {"type": "default_branch_is", "branch": branch},
                ],
                authorization=Authorization(
                    required=(mode == Mode.APPLY),
                    status="NOT_REQUIRED" if mode != Mode.APPLY else "PENDING",
                ),
                action={
                    "type": "READ"
                    if mode in (Mode.PLAN, Mode.VERIFY, Mode.ASSURE)
                    else "WRITE",
                    "target": f"{owner}/{repo}:{branch}",
                    "desired_rules": self.desired.get("branch_protection", {}),
                },
                postconditions=[
                    {"type": "rules_match_desired"},
                    {"type": "force_push_disabled"},
                    {"type": "required_checks_exist"},
                ],
            )
        )

        # G1 — Collaborator permissions (placeholder for expansion)
        ops.append(
            OperationRecord(
                operation_id="ATO-GH-BOOTSTRAP-001.G1.COLLABORATORS",
                feature="github.collaborators",
                mode=mode,
                desired_state_revision=rev,
                preconditions=[
                    {"type": "repo_exists", "owner": owner, "repo": repo},
                ],
                authorization=Authorization(
                    required=(mode == Mode.APPLY),
                    status="NOT_REQUIRED" if mode != Mode.APPLY else "PENDING",
                ),
                action={
                    "type": "READ"
                    if mode in (Mode.PLAN, Mode.VERIFY, Mode.ASSURE)
                    else "WRITE",
                    "target": f"{owner}/{repo}",
                    "desired_permissions": self.desired.get("permissions", {}),
                },
                postconditions=[
                    {"type": "permissions_match_manifest"},
                    {"type": "no_unapproved_admins"},
                ],
            )
        )

        return ops
