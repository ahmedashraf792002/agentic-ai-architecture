import concurrent.futures
import logging
import uuid
from pathlib import Path

from agents.reconciler import reconcile, write_reconciliation_report
from agents.subagents.business_analyst import build_standalone as build_business
from agents.subagents.code_analyzer import build_standalone as build_code
from agents.subagents.infra_analyzer import build_standalone as build_infra
from agents.subagents.integration_mapper import build_standalone as build_integration
from agents.subagents.strategy_analyst import build_standalone as build_strategy
from agents.validator import validate, write_validation_report
from backend.git_ops import commit_to_model
from backend.pr_ops import open_pull_request

logger = logging.getLogger(__name__)


def run_subagent(build_fn, system_id, evidence_root, systems_root):
    agent = build_fn(
        system_id=system_id,
        evidence_root=evidence_root,
        systems_root=systems_root,
    )
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                "Analyze all available evidence and produce the corresponding "
                "ArchiMate elements (or relationships) according to your "
                "system prompt."
            ),
        }]
    })
    return result["messages"][-1].content if result.get("messages") else str(result)


def run_as_is_ingestion(
    system_id: str,
    evidence_path: str | Path,
    systems_root: str | Path,
    github_token: str,
    github_model_repo: str,
    system_id_int: int | None = None,
    db_session=None,
    run_id: str | None = None,
):

    evidence_path = Path(evidence_path)
    systems_root = Path(systems_root)
    run_id = run_id or str(uuid.uuid4())[:8]

    logger.info("[%s] Starting ingestion for system=%s", run_id, system_id)

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        subagents = [
            ("strategy-analyst", build_strategy),
            ("business-analyst", build_business),
            ("code-analyzer", build_code),
            ("infra-analyzer", build_infra),
        ]
        futures = {
            pool.submit(run_subagent, fn, system_id, str(evidence_path), str(systems_root)): name
            for name, fn in subagents
        }
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                future.result()
                logger.info("[%s] %s completed", run_id, name)
            except Exception as exc:
                logger.error("[%s] %s failed: %s", run_id, name, exc)
                raise

    logger.info("[%s] Running integration-mapper", run_id)
    run_subagent(build_integration, system_id, str(evidence_path), str(systems_root))

    
    logger.info("[%s] Running reconciler", run_id)
    rec_result = reconcile(systems_root, system_id)
    write_reconciliation_report(systems_root, system_id, rec_result)
    logger.info(
        "[%s] Reconciler: merged=%d conflicts=%d",
        run_id, rec_result.merged_count, len(rec_result.conflicts),
    )
    
    logger.info("[%s] Running validator", run_id)
    report = validate(systems_root, system_id)
    write_validation_report(systems_root, system_id, report)

    if not report.passed:
        logger.error("[%s] Validation FAILED: %d violations", run_id, len(report.violations))
        raise RuntimeError(
            f"Validation failed: {len(report.violations)} violations, "
            f"{len(report.needs_review)} items flagged for review"
        )

    logger.info("[%s] Committing to git", run_id)
    remote = f"https://github.com/{github_model_repo}.git"
    commit_result = commit_to_model(
        working_tree=systems_root,
        system_id=system_id,
        run_id=run_id,
        github_token=github_token,
        remote_url=remote,
    )

    
    logger.info("[%s] Opening Pull Request", run_id)
    pr_result = open_pull_request(
        session=db_session,
        repo=github_model_repo,
        branch=commit_result.branch,
        commit_sha=commit_result.commit_sha,
        system_id=system_id_int or 1,
        run_id=run_id,
        report=report,
        github_token=github_token,
    )

    logger.info("[%s] PR #%d opened: %s", run_id, pr_result.pr_number, pr_result.pr_url)
    return {
        "run_id": run_id,
        "status": "succeeded",
        "commit_sha": commit_result.commit_sha,
        "pr_number": pr_result.pr_number,
        "pr_url": pr_result.pr_url,
    }
