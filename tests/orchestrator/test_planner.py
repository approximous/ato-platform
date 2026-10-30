from pathlib import Path
from ato_foundation.orchestrator.planner import Planner
from ato_foundation.models import Mode


def test_plan_produces_operations():
    config = Path(__file__).resolve().parents[2] / "config" / "github-desired-state.yaml"
    planner = Planner(str(config))
    ops = planner.plan_github_bootstrap(mode=Mode.VERIFY)
    assert len(ops) >= 1
    assert any(op.operation_id.startswith("ATO-GH-BOOTSTRAP-001.G2") for op in ops)
    assert all(op.mode == Mode.VERIFY for op in ops)
