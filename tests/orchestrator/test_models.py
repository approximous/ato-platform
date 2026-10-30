from ato_foundation.models import (
    Mode,
    Classification,
    Disposition,
    EvidenceRecord,
    OperationRecord,
    Authorization,
)


def test_evidence_record_hash_stable():
    obs = {"key": "value", "num": 42}
    r1 = EvidenceRecord.create(Classification.VERIFIED, "test.subject", obs)
    r2 = EvidenceRecord.create(Classification.VERIFIED, "test.subject", obs)
    # Same content → same hash (different IDs/timestamps are expected)
    assert r1.evidence_hash == r2.evidence_hash


def test_operation_record_to_dict():
    op = OperationRecord(
        operation_id="TEST.001",
        feature="test.feature",
        mode=Mode.VERIFY,
        desired_state_revision="0.1.0",
        authorization=Authorization(required=False, status="NOT_REQUIRED"),
    )
    d = op.to_dict()
    assert d["mode"] == "VERIFY"
    assert d["classification"] == "UNTESTED"
    assert d["disposition"] == "INDETERMINATE"
