import os
import subprocess
import time
from pathlib import Path

import pytest
from dotenv import load_dotenv

from backend.git_ops import commit_to_model

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_MODEL_REPO = os.environ.get("GITHUB_MODEL_REPO")

pytestmark = pytest.mark.skipif(
    not GITHUB_TOKEN or not GITHUB_MODEL_REPO,
    reason="GITHUB_TOKEN and GITHUB_MODEL_REPO must be set in .env to run the live G1 test",
)


def run(args: list[str], cwd: Path):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def remote_url():
    return f"https://github.com/{GITHUB_MODEL_REPO}.git"


def delete_remote_branch(working_tree: Path, branch: str):
    authenticated = remote_url().replace("https://", f"https://x-access-token:{GITHUB_TOKEN}@", 1)
    subprocess.run(
        ["git", "push", authenticated, "--delete", branch],
        cwd=working_tree,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture()
def cloned_repo(tmp_path: Path):
    working_tree = tmp_path / "model-repo"
    authenticated = remote_url().replace("https://", f"https://x-access-token:{GITHUB_TOKEN}@", 1)
    subprocess.run(
        ["git", "clone", authenticated, str(working_tree)],
        capture_output=True,
        text=True,
        check=True,
    )
    run(["config", "user.email", "test@example.com"], cwd=working_tree)
    run(["config", "user.name", "Live Test"], cwd=working_tree)
    return working_tree


def test_commit_to_model_against_real_github(cloned_repo: Path):
    run_id = f"live-test-{int(time.time())}"
    system_id = "legacy-system"
    branch = f"feature/ingest-{system_id}-{run_id}"

    element_dir = cloned_repo / "systems" / system_id / "as-is" / "application"
    element_dir.mkdir(parents=True, exist_ok=True)
    (element_dir / "_live_test_probe.json").write_text('{"probe": true}', encoding="utf-8")

    try:
        result = commit_to_model(
            working_tree=cloned_repo,
            system_id=system_id,
            run_id=run_id,
            github_token=GITHUB_TOKEN,
            remote_url=remote_url(),
        )

        assert result.created is True
        assert result.branch == branch
        assert result.commit_sha

        remote_branches = subprocess.run(
            ["git", "ls-remote", "--heads", remote_url().replace("https://", f"https://x-access-token:{GITHUB_TOKEN}@", 1)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert branch in remote_branches

        second = commit_to_model(
            working_tree=cloned_repo,
            system_id=system_id,
            run_id=run_id,
            github_token=GITHUB_TOKEN,
            remote_url=remote_url(),
        )
        assert second.created is False
        assert second.commit_sha == result.commit_sha

    finally:
    
        delete_remote_branch(cloned_repo, branch)