# ATO Foundation — Operation Orchestrator

Evidence-driven automation control plane for the Android Threat Observatory (ATO) / Android Adversarial Security Lab.

This repository implements the **Build Plane** (Stages 0–1) of the progressive density bootstrap:

- Strict OperationRecord contract (preconditions → authorized action → postconditions → independent verification → evidence → disposition)
- Four modes: `PLAN` / `VERIFY` / `APPLY` / `ASSURE`
- Five evidence classifications: `VERIFIED` / `REPORTED` / `INFERRED` / `BLOCKED` / `UNTESTED`
- Gate model (G1–G5) for ATO-GH-BOOTSTRAP-001
- Mock GitHub client for fully offline development and testing

## Current Status

| Stage | Description                        | Status   |
|-------|------------------------------------|----------|
| 0     | Core models + project skeleton     | Complete |
| 1     | Mock runtime (Planner/Executor/Verifier/Gates) | Complete |
| 2     | Real GitHub VERIFY/ASSURE          | Next     |
| 3+    | Controlled APPLY + further features| Future   |

## Quick Start (Stage 1 — Mock)

```bash
# From repository root
python -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Run the bootstrap in VERIFY mode against the in-memory mock
python scripts/run_bootstrap.py

# Run unit tests
pytest -v
```

## Project Layout

```
ato-platform/
├── config/                  # Desired-state manifests (data, not code)
├── src/ato_foundation/
│   ├── models.py            # OperationRecord, EvidenceRecord, enums
│   ├── orchestrator/        # Planner, GateEngine, Executor, Verifier
│   ├── github/              # Client abstraction + Mock
│   └── evidence/            # Append-only ledger
├── scripts/run_bootstrap.py
├── tests/
└── evidence/                # Generated ledger (gitignored in real use)
```

## Design Principles

1. **No self-declared success** — only independent verification can produce `VERIFIED`.
2. **Fail-closed** — missing preconditions, missing approval, or verification failure → `BLOCKED` / `REQUIRE_HUMAN`.
3. **Desired state is data** — behaviour changes by editing YAML, not by changing orchestrator code.
4. **Progressive density** — capability is added only after the previous stage’s gates are `QUALIFIED`.

## Next Steps

1. Expand `Planner` and `Verifier` to cover every criterion in ATO-GH-BOOTSTRAP-001.
2. Implement a real (least-privilege) `GitHubClient`.
3. Add human-approval gate for `APPLY` mode.
4. Promote Stages 2–4 through the same evidence-gated process.

## License

Apache-2.0
