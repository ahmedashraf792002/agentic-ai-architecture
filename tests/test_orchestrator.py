from unittest.mock import MagicMock, patch

import pytest

from agents.validator import ValidationReport


@pytest.fixture()
def mock_commit():
    return MagicMock(branch="feature/ingest-sys1-test", created=True, commit_sha="abc123")


@pytest.fixture()
def mock_pr():
    return MagicMock(pr_number=42, pr_url="https://github.com/test/repo/pull/42")


def test_orchestrator_runs_full_pipeline(db_session, legacy_system, mock_commit, mock_pr, tmp_path):
    with patch("agents.orchestrator.build_strategy") as bs, \
         patch("agents.orchestrator.build_business") as _bb, \
         patch("agents.orchestrator.build_code") as _bc, \
         patch("agents.orchestrator.build_infra") as _bi, \
         patch("agents.orchestrator.build_integration") as _bint, \
         patch("agents.orchestrator.reconcile") as rec, \
         patch("agents.orchestrator.validate") as val, \
         patch("agents.orchestrator.write_validation_report") as _wvr, \
         patch("agents.orchestrator.write_reconciliation_report") as _wrr, \
         patch("agents.orchestrator.commit_to_model") as ctm, \
         patch("agents.orchestrator.open_pull_request") as opr:

        agent_mock = MagicMock()
        agent_mock.invoke.return_value = {"messages": [MagicMock(content="ok")]}
        bs.return_value = agent_mock

        rec.return_value = MagicMock(merged_count=0, conflicts=[])
        val.return_value = ValidationReport(passed=True, counts_by_layer={"application": 1})
        ctm.return_value = mock_commit
        opr.return_value = mock_pr

        from agents.orchestrator import run_as_is_ingestion
        result = run_as_is_ingestion(
            system_id="sys1",
            evidence_path=str(tmp_path / "evidence"),
            systems_root=str(tmp_path / "systems"),
            github_token="fake-token",
            github_model_repo="test/repo",
            system_id_int=legacy_system.id,
            db_session=db_session,
        )

    assert result["status"] == "succeeded"
    assert result["pr_number"] == 42
    assert result["commit_sha"] == "abc123"
    assert len(result["run_id"]) == 8


def test_orchestrator_stops_on_validation_failure(db_session, legacy_system, tmp_path):
    from agents.orchestrator import run_as_is_ingestion

    with patch("agents.orchestrator.build_strategy") as bs, \
         patch("agents.orchestrator.build_business") as _bb, \
         patch("agents.orchestrator.build_code") as _bc, \
         patch("agents.orchestrator.build_infra") as _bi, \
         patch("agents.orchestrator.build_integration") as _bint, \
         patch("agents.orchestrator.reconcile") as rec, \
         patch("agents.orchestrator.validate") as val, \
         patch("agents.orchestrator.write_validation_report") as _wvr, \
         patch("agents.orchestrator.write_reconciliation_report") as _wrr:

        agent_mock = MagicMock()
        agent_mock.invoke.return_value = {"messages": [MagicMock(content="ok")]}
        bs.return_value = agent_mock

        rec.return_value = MagicMock(merged_count=0, conflicts=[])
        val.return_value = ValidationReport(
            passed=False,
            violations=[{"path": "test.json", "error": "invalid type"}],
        )

        with pytest.raises(RuntimeError, match="Validation failed"):
            run_as_is_ingestion(
                system_id="sys1",
                evidence_path=str(tmp_path / "evidence"),
                systems_root=str(tmp_path / "systems"),
                github_token="fake-token",
                github_model_repo="test/repo",
                system_id_int=legacy_system.id,
                db_session=db_session,
            )


def test_orchestrator_raises_on_subagent_failure(db_session, legacy_system, tmp_path):
    from agents.orchestrator import run_as_is_ingestion

    with patch("agents.orchestrator.build_strategy") as bs, \
         patch("agents.orchestrator.build_business") as _bb, \
         patch("agents.orchestrator.build_code") as _bc, \
         patch("agents.orchestrator.build_infra") as _bi:

        bs.side_effect = RuntimeError("strategy agent failed")

        with pytest.raises(RuntimeError, match="strategy agent failed"):
            run_as_is_ingestion(
                system_id="sys1",
                evidence_path=str(tmp_path / "evidence"),
                systems_root=str(tmp_path / "systems"),
                github_token="fake-token",
                github_model_repo="test/repo",
                system_id_int=legacy_system.id,
                db_session=db_session,
            )
