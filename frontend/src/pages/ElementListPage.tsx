import { useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError, type ModelElementSummary } from "../api/client";

const LAYER_ORDER = ["motivation", "strategy", "business", "application", "technology"];

function groupByLayer(elements: ModelElementSummary[]): Map<string, ModelElementSummary[]> {
  const groups = new Map<string, ModelElementSummary[]>();
  for (const element of elements) {
    const bucket = groups.get(element.layer) ?? [];
    bucket.push(element);
    groups.set(element.layer, bucket);
  }
  return groups;
}

export default function ElementListPage() {
  const [systemId, setSystemId] = useState("1");
  const [elements, setElements] = useState<ModelElementSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleLoad() {
    setError(null);
    setIsLoading(true);
    try {
      const data = await api.listElements(Number(systemId));
      setElements(data);
    } catch (err) {
      setElements(null);
      setError(err instanceof ApiError ? err.message : "Failed to load elements.");
    } finally {
      setIsLoading(false);
    }
  }

  const grouped = elements ? groupByLayer(elements) : null;
  const layers = grouped
    ? [...LAYER_ORDER.filter((l) => grouped.has(l)), ...[...grouped.keys()].filter((l) => !LAYER_ORDER.includes(l))]
    : [];

  return (
    <div className="page">
      <h1>Model Elements</h1>

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

      {grouped &&
        layers.map((layer) => (
          <section key={layer} className="layer-group" data-testid={`layer-group-${layer}`}>
            <h2>{layer}</h2>
            <ul className="element-list">
              {grouped.get(layer)!.map((el) => (
                <li key={el.id}>
                  <Link to={`/elements/${el.id}`}>
                    {el.name} <span className="type-tag">{el.archimate_type}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}

      {grouped && layers.length === 0 && <p>No elements found for this system.</p>}
    </div>
  );
}
