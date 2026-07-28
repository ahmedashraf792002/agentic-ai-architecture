import os
import subprocess
from pathlib import Path

import pytest

SYSTEM_ID = "sample-system"
EVIDENCE_ROOT = Path("evidence")
SYSTEMS_ROOT = Path("systems")


def run(args: list[str], cwd: Path):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=120, check=False)


def test_evidence_set_exists():
    assert EVIDENCE_ROOT.exists()
    subdirs = ["strategy", "motivation", "business", "code", "infra", "integration"]
    for d in subdirs:
        assert (EVIDENCE_ROOT / d).exists(), f"missing evidence/{d}"
        files = list((EVIDENCE_ROOT / d).iterdir())
        assert len(files) > 0, f"no files in evidence/{d}"


def test_subagents_produce_elements(tmp_path):
    systems_root = tmp_path / "systems"
    systems_root.mkdir()
    system_dir = systems_root / SYSTEM_ID / "as-is"
    system_dir.mkdir(parents=True)

    from agents.subagents.business_analyst import build_standalone as build_business
    from agents.subagents.code_analyzer import build_standalone as build_code
    from agents.subagents.infra_analyzer import build_standalone as build_infra
    from agents.subagents.strategy_analyst import build_standalone as build_strategy

    subagents = [
        ("strategy", build_strategy),
        ("business", build_business),
        ("code", build_code),
        ("infra", build_infra),
    ]

    for name, builder in subagents:
        agent = builder(
            system_id=SYSTEM_ID,
            evidence_root=str(EVIDENCE_ROOT),
            systems_root=str(systems_root),
        )
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": (
                    "Analyze all available evidence and produce the corresponding "
                    "ArchiMate elements according to your system prompt."
                ),
            }]
        })
        assert result.get("messages"), f"{name} agent produced no messages"

    element_files = list(system_dir.glob("*/*.json"))
    assert len(element_files) >= 3, f"expected at least 3 element files, got {len(element_files)}"

    from agents.reconciler import reconcile
    rec_result = reconcile(systems_root, SYSTEM_ID)
    assert rec_result.merged_count >= 0

    from agents.validator import validate
    report = validate(systems_root, SYSTEM_ID)
    assert report.passed, f"validation failed: {report.violations}"


@pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN") or not os.environ.get("GITHUB_MODEL_REPO"),
    reason="GITHUB_TOKEN and GITHUB_MODEL_REPO required",
)
def test_e2e_full_pipeline(db_session, legacy_system, tmp_path):
    systems_root = tmp_path / "systems"
    systems_root.mkdir()

    from agents.orchestrator import run_as_is_ingestion

    result = run_as_is_ingestion(
        system_id=SYSTEM_ID,
        evidence_path=str(EVIDENCE_ROOT),
        systems_root=str(systems_root),
        github_token=os.environ["GITHUB_TOKEN"],
        github_model_repo=os.environ["GITHUB_MODEL_REPO"],
        system_id_int=legacy_system.id,
        db_session=db_session,
    )

    assert result["status"] == "succeeded"
    assert result["pr_number"] > 0
    assert result["commit_sha"]
    assert result["pr_url"].startswith("https://github.com/")
