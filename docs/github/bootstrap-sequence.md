# ATO-GH-BOOTSTRAP-001 Sequence

## Gates

- **G1** — Authority established (collaborators, ownership)
- **G2** — Security baseline established (branch protection, security features, Actions permissions)
- **G3** — Source published
- **G4** — CI qualified
- **G5** — Independent assurance completed

## Modes

| Mode   | Writes? | Purpose                          |
|--------|---------|----------------------------------|
| PLAN   | No      | Calculate intended changes       |
| VERIFY | No      | Observe actual vs desired state  |
| APPLY  | Yes     | Execute only authorized changes  |
| ASSURE | No      | Full independent evaluation      |

## Evidence Contract

Every operation produces an `OperationRecord` containing:

- Preconditions
- Authorization status
- Exact authorized action
- Observations (read-back)
- Postconditions evaluation
- One or more `EvidenceRecord`s with classification and content hash
- Final disposition
