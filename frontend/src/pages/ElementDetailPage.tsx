import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError, buildGitHubBlobUrl, type ModelElementDetail } from "../api/client";

export default function ElementDetailPage() {
  const { elementId } = useParams<{ elementId: string }>();
  const [element, setElement] = useState<ModelElementDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!elementId) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    api
      .getElement(elementId)
      .then((data) => {
        if (!cancelled) setElement(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Failed to load element.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [elementId]);

  if (isLoading) return <div className="page">Loading…</div>;
  if (error) return <div className="page error-text">{error}</div>;
  if (!element) return <div className="page">Element not found.</div>;

  return (
    <div className="page">
      <p>
        <Link to="/elements">&larr; Back to elements</Link>
      </p>
      <h1>{element.name}</h1>
      <p className="type-tag">
        {element.layer} / {element.archimate_type}
      </p>
      <p className="confidence-tag" data-testid="confidence">
        Confidence: {element.confidence}
      </p>

      <h2>Documentation</h2>
      <p data-testid="documentation">{element.documentation || "—"}</p>

      <h2>Evidence citations</h2>
      {element.evidence.length === 0 && <p>No evidence citations.</p>}
      <ul className="evidence-list" data-testid="evidence-list">
        {element.evidence.map((e, i) => {
          const link = buildGitHubBlobUrl(element.current_commit, e.locator);
          return (
            <li key={i} data-testid="evidence-item">
              <strong>{e.source_type}</strong>{" "}
              {link ? (
                <a href={link} target="_blank" rel="noreferrer">
                  {e.locator}
                </a>
              ) : (
                <span>{e.locator}</span>
              )}
              {e.excerpt && <blockquote>{e.excerpt}</blockquote>}
            </li>
          );
        })}
      </ul>

      <h2>Relationships</h2>
      {element.relationships.length === 0 && <p>No relationships.</p>}
      <ul className="relationship-list" data-testid="relationship-list">
        {element.relationships.map((r, i) => (
          <li key={i}>
            <span className="type-tag">{r.type}</span>{" "}
            <Link to={`/elements/${r.target_id}`}>{r.target_id}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
