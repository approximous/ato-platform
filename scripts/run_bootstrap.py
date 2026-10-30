#!/usr/bin/env python3
"""Minimal runner for ATO-GH-BOOTSTRAP-001 (Stage 0/1 — mock only)."""

from pathlib import Path
import sys

# Allow running from repository root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ato_foundation.github.client import MockGitHubClient
from ato_foundation.orchestrator.planner import Planner
from ato_foundation.orchestrator.executor import Executor
from ato_foundation.orchestrator.verifier import Verifier
from ato_foundation.orchestrator.gate_engine import GateEngine
from ato_foundation.evidence.ledger import EvidenceLedger
from ato_foundation.models import Mode


def main() -> None:
    client = MockGitHubClient()

    # Seed a repository that partially matches desired state
    client.seed_repository("ato-platform", "ato", {"default_branch": "main"})
    client.seed_branch_protection(
        "ato-platform",
        "ato",
        "main",
        {
            "enforce_admins": True,
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
            },
            "allow_force_pushes": False,
            "allow_deletions": False,
        },
    )

    config_path = Path(__file__).resolve().parents[1] / "config" / "github-desired-state.yaml"
    planner = Planner(str(config_path))
    ledger = EvidenceLedger(path="evidence/ledger.jsonl")
    verifier = Verifier(client)
    executor = Executor(client, verifier, ledger)
    gates = GateEngine()

    print("=== ATO-GH-BOOTSTRAP-001 (VERIFY mode, mock client) ===\n")

    plan = planner.plan_github_bootstrap(mode=Mode.VERIFY)
    print(f"Planned {len(plan)} operations\n")

    results = []
    for op in plan:
        result = executor.run(op)
        results.append(result)
        status = f"{result.disposition.value:12} / {result.classification.value}"
        print(f"{result.operation_id}")
        print(f"  → {status}")
        if result.error:
            print(f"  error: {result.error}")
        print()

    gate_status = gates.evaluate(results)
    print("=== Gate Status ===")
    for g, s in gate_status.items():
        print(f"  {g}: {s}")

    print(f"\nEvidence written to: {ledger.path}")


if __name__ == "__main__":
    main()
