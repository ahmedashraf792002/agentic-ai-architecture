from dataclasses import dataclass
import httpx
from agents.validator import ValidationReport
from backend.repository.artifact_versions import create_artifact_version


class PullRequestError(Exception):
    pass


@dataclass
class PullRequestResult:
    pr_number: int
    pr_url: str


def _build_pr_body(report: ValidationReport, run_id: str) :
    lines = [f"Automated As-Is ingestion — run `{run_id}`", "", "## Element counts"]
    for layer, count in sorted(report.counts_by_layer.items()):
        lines.append(f"- {layer}: {count}")

    if report.needs_review:
        lines.append("")
        lines.append("## Flagged for review")
        for item in report.needs_review:
            lines.append(f"- {item['path']}: {item['reason']}")

    if not report.passed:
        lines.append("")
        lines.append("## Violations")
        for violation in report.violations:
            lines.append(f"- {violation['path']}: {violation['error']}")

    return "\n".join(lines)


def open_pull_request(
    session,
    repo: str,
    branch: str,
    commit_sha: str,
    system_id: str,
    run_id: str,
    report: ValidationReport,
    github_token: str,
    base_branch: str = "main",
    client: httpx.Client | None = None,
) :
    body = _build_pr_body(report, run_id)
    title = f"As-Is ingestion: {system_id} ({run_id})"
    owns_client = client is None
    client = client or httpx.Client()

    try:
        response = client.post(
            f"https://api.github.com/repos/{repo}/pulls",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
            json={"title": title, "head": branch, "base": base_branch, "body": body},
            timeout=30.0,
        )
    finally:
        if owns_client:
            client.close()

    if response.status_code != 201:
        raise PullRequestError(f"GitHub PR creation failed: {response.status_code} {response.text}")

    data = response.json()
    pr_number = data["number"]
    pr_url = data["html_url"]

    create_artifact_version(
        session,
        system_id=system_id,
        commit_sha=commit_sha,
        phase="as-is",
        author_type="agent",
        run_id=run_id,
        pr_number=pr_number,
    )

    return PullRequestResult(pr_number=pr_number, pr_url=pr_url)
