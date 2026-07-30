import { useState } from "react";
import { api, ApiError, type ArtifactVersion } from "../api/client";

const STATUS_COLOR: Record<string, string> = {
  pending: "#8a8f98",
  approved: "#16a34a",
  rejected: "#dc2626",
};

function shortSha(sha: string): string {
  return sha.slice(0, 7);
}

function githubRepo(): string {
  return import.meta.env.VITE_GITHUB_REPO ?? "";
}

function buildPrUrl(prNumber: number | null): string | null {
  const repo = githubRepo();
  if (!repo || prNumber === null) return null;
  return `https://github.com/${repo}/pull/${prNumber}`;
}

export default function ArtifactVersionsPage() {
  const [systemId, setSystemId] = useState("1");
  const [versions, setVersions] = useState<ArtifactVersion[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleLoad() {
    setError(null);
    setIsLoading(true);
    try {
      const data = await api.listArtifactVersions(Number(systemId));
      setVersions(data);
    } catch (err) {
      setVersions(null);
      setError(err instanceof ApiError ? err.message : "Failed to load artifact versions.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Artifact Versions</h1>

      <div className="form-row">
        <label>
          System ID
          <input value={systemId} onChange={(e) => setSystemId(e.target.value)} />
        </label>
        <button onClick={handleLoad} disabled={isLoading}>
          {isLoading ? "Loading…" : "Load"}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {versions && versions.length === 0 && <p>No artifact versions for this system.</p>}

      {versions && versions.length > 0 && (
        <table className="versions-table" data-testid="versions-table">
          <thead>
            <tr>
              <th>Commit</th>
              <th>Phase</th>
              <th>Status</th>
              <th>Pull Request</th>
            </tr>
          </thead>
          <tbody>
            {versions.map((v) => {
              const prUrl = buildPrUrl(v.pr_number);
              return (
                <tr key={v.id} data-testid="version-row">
                  <td>
                    <code>{shortSha(v.commit_sha)}</code>
                  </td>
                  <td>{v.phase}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: STATUS_COLOR[v.approval_status] ?? "#8a8f98" }}
                    >
                      {v.approval_status}
                    </span>
                  </td>
                  <td>
                    {v.pr_number === null ? (
                      "—"
                    ) : prUrl ? (
                      <a href={prUrl} target="_blank" rel="noreferrer">
                        #{v.pr_number}
                      </a>
                    ) : (
                      `#${v.pr_number}`
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
