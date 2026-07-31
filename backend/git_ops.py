import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitOperationError(Exception):
    pass


@dataclass
class CommitResult:
    branch: str
    created: bool
    commit_sha: str


def _run_git(args: list[str], cwd: Path):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _scrub_token(text: str, token: str):
    return text.replace(token, "***") if token else text


def _authenticated_remote(remote_url: str, token: str):
    if remote_url.startswith("https://"):
        return remote_url.replace(
            "https://",
            f"https://x-access-token:{token}@",
            1,
        )
    return remote_url


def _remote_branch_sha(working_tree: Path, remote: str, branch: str):
    result = _run_git(
        ["ls-remote", "--heads", remote, branch],
        cwd=working_tree,
    )

    if result.returncode != 0 or not result.stdout.strip():
        return None

    return result.stdout.split()[0]


def commit_to_model(
    working_tree: str | Path,
    system_id: str,
    run_id: str,
    github_token: str,
    remote_url: str,
):
    working_tree = Path(working_tree)
    print("Working tree:", working_tree)

    branch = f"feature/ingest-{system_id}-{run_id}"

    authenticated_remote = _authenticated_remote(
        remote_url,
        github_token,
    )

    existing_sha = _remote_branch_sha(
        working_tree,
        authenticated_remote,
        branch,
    )

    if existing_sha is not None:
        return CommitResult(
            branch=branch,
            created=False,
            commit_sha=existing_sha,
        )

    checkout = _run_git(
        ["checkout", "-B", branch],
        cwd=working_tree,
    )

    if checkout.returncode != 0:
        raise GitOperationError(
            _scrub_token(checkout.stderr, github_token)
        )

    # Stage everything
    add = _run_git(["add", "-A"], cwd=working_tree)
    if add.returncode != 0:
        raise GitOperationError(
            _scrub_token(add.stderr, github_token)
        )

    # Never commit secrets
    _run_git(
        ["rm", "--cached", "--ignore-unmatch", ".env"],
        cwd=working_tree,
    )

    commit_message = f"Ingest run {run_id} for system {system_id}"

    commit = _run_git(
        [
            "-c",
            "user.name=Ahmed Ashraf",
            "-c",
            "user.email=117744931+ahmedashraf792002@users.noreply.github.com",
            "commit",
            "-m",
            commit_message,
        ],
        cwd=working_tree,
    )

    if (
        commit.returncode != 0
        and "nothing to commit" not in commit.stdout.lower()
    ):
        raise GitOperationError(
            _scrub_token(commit.stderr, github_token)
        )

    rev_parse = _run_git(
        ["rev-parse", "HEAD"],
        cwd=working_tree,
    )

    if rev_parse.returncode != 0:
        raise GitOperationError(
            _scrub_token(rev_parse.stderr, github_token)
        )

    print("Commit SHA:", rev_parse.stdout.strip())

    push = _run_git(
        ["push", authenticated_remote, branch],
        cwd=working_tree,
    )

    if push.returncode != 0:
        raise GitOperationError(
            _scrub_token(push.stderr, github_token)
        )

    return CommitResult(
        branch=branch,
        created=True,
        commit_sha=rev_parse.stdout.strip(),
    )