import os
import subprocess
import time
from pathlib import Path

import httpx
import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agents.validator import ValidationReport
from backend.git_ops import commit_to_model
from backend.pr_ops import open_pull_request
from backend.repository.legacy_systems import create_legacy_system
from backend.repository.artifact_versions import list_artifact_versions
from backend.database import engine

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_MODEL_REPO = os.environ.get("GITHUB_MODEL_REPO")

pytestmark = pytest.mark.skipif(
    not GITHUB_TOKEN or not GITHUB_MODEL_REPO,
    reason="GITHUB_TOKEN and GITHUB_MODEL_REPO must be set in .env to run the live G2 test",
)


def remote_url():
    return f"https://github.com/{GITHUB_MODEL_REPO}.git"


def authenticated_remote():
    return remote_url().replace("https://", f"https://x-access-token:{GITHUB_TOKEN}@", 1)

def close_and_delete_branch(pr_number: int, branch: str, working_tree: Path):
    httpx.patch(
        f"https://api.github.com/repos/{GITHUB_MODEL_REPO}/pulls/{pr_number}",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"},
        json={"state": "closed"},
        timeout=30.0,
    )
    subprocess.run(
        ["git", "push", authenticated_remote(), "--delete", branch],
        cwd=working_tree,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def legacy_system(db_session):
    return create_legacy_system(db_session,name="Live Test System")


@pytest.fixture()
def cloned_repo(tmp_path: Path):
    working_tree = tmp_path / "model-repo"
    subprocess.run(
        ["git", "clone", authenticated_remote(), str(working_tree)],
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=working_tree, check=True)
    subprocess.run(["git", "config", "user.name", "Live Test"], cwd=working_tree, check=True)
    return working_tree


def test_open_pull_request_against_real_github(cloned_repo: Path, db_session, legacy_system):
    run_id = f"live-pr-test-{int(time.time())}"
    system_id_slug = "legacy-system"

    element_dir = cloned_repo / "systems" / system_id_slug / "as-is" / "application"
    element_dir.mkdir(parents=True, exist_ok=True)
    (element_dir / "_live_pr_test_probe.json").write_text('{"probe": true}', encoding="utf-8")

    commit_result = commit_to_model(
        working_tree=cloned_repo,
        system_id=system_id_slug,
        run_id=run_id,
        github_token=GITHUB_TOKEN,
        remote_url=remote_url(),
    )
    assert commit_result.created is True

    report = ValidationReport()
    report.counts_by_layer = {"application": 1}
    report.passed = True

    pr_result = None

    try:
        pr_result = open_pull_request(
            db_session,
            repo=GITHUB_MODEL_REPO,
            branch=commit_result.branch,
            commit_sha=commit_result.commit_sha,
            system_id=legacy_system.id,
            run_id=run_id,
            report=report,
            github_token=GITHUB_TOKEN,
        )

        assert pr_result.pr_number > 0
        assert pr_result.pr_url.startswith(f"https://github.com/{GITHUB_MODEL_REPO}/pull/")

        versions = list_artifact_versions(db_session, legacy_system.id)
        assert len(versions) == 1
        assert versions[0].approval_status == "pending"
        assert versions[0].commit_sha == commit_result.commit_sha

    finally:
        if pr_result is not None:
            close_and_delete_branch(pr_result.pr_number, commit_result.branch, cloned_repo)
        else:
            subprocess.run(
                ["git", "push", authenticated_remote(), "--delete", commit_result.branch],
                cwd=cloned_repo,
                capture_output=True,
                text=True,
                check=False,
            )
