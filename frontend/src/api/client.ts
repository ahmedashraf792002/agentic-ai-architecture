const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": import.meta.env.VITE_API_KEY ?? "",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body || response.statusText);
  }

  return response.json() as Promise<T>;
}

export interface IngestResponse {
  job_id: number;
  run_id: string;
  status: string;
}

export interface JobStatus {
  id: number;
  status: "queued" | "running" | "succeeded" | "failed";
  run_id: string | null;
  error_message: string | null;
}

export interface ModelElementSummary {
  id: string;
  layer: string;
  archimate_type: string;
  name: string;
}

export interface EvidenceCitation {
  source_type: string;
  locator: string;
  excerpt?: string;
}

export interface RelationshipRef {
  target_id: string;
  type: string;
}

export interface ModelElementDetail {
  id: string;
  layer: string;
  archimate_type: string;
  name: string;
  documentation: string;
  confidence: string;
  evidence: EvidenceCitation[];
  relationships: RelationshipRef[];
  current_commit?: string;
}

export interface ArtifactVersion {
  id: number;
  commit_sha: string;
  phase: string;
  pr_number: number | null;
  approval_status: string;
}

export const api = {
  triggerIngest: (systemId: number, evidencePath: string): Promise<IngestResponse> =>
    request<IngestResponse>(
      `/systems/${systemId}/ingest?evidence_path=${encodeURIComponent(evidencePath)}`,
      { method: "POST" },
    ),

  getJobStatus: (jobId: number): Promise<JobStatus> => request<JobStatus>(`/jobs/${jobId}`),

  listElements: (systemId: number, layer?: string): Promise<ModelElementSummary[]> => {
    const query = layer ? `?layer=${encodeURIComponent(layer)}` : "";
    return request<ModelElementSummary[]>(`/systems/${systemId}/elements${query}`);
  },

  getElement: (elementId: string): Promise<ModelElementDetail> =>
    request<ModelElementDetail>(`/elements/${elementId}`),

  listArtifactVersions: (systemId: number): Promise<ArtifactVersion[]> =>
    request<ArtifactVersion[]>(`/systems/${systemId}/artifact-versions`),
};

export { ApiError, API_BASE_URL };

export function buildGitHubBlobUrl(commit: string | undefined, locator: string): string | null {
  const githubRepo = import.meta.env.VITE_GITHUB_REPO;
  if (!githubRepo || !commit) {
    return null;
  }
  const cleanPath = locator.startsWith("/") ? locator.slice(1) : locator;
  return `https://github.com/${githubRepo}/blob/${commit}/${cleanPath}`;
}
