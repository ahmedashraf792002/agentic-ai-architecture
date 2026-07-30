import { useEffect, useRef, useState } from "react";
import { api, ApiError, type JobStatus } from "../api/client";

const POLL_INTERVAL_MS = 3000;

const STATUS_LABEL: Record<JobStatus["status"], string> = {
  queued: "Queued",
  running: "Running…",
  succeeded: "Succeeded",
  failed: "Failed",
};

const STATUS_COLOR: Record<JobStatus["status"], string> = {
  queued: "#8a8f98",
  running: "#2563eb",
  succeeded: "#16a34a",
  failed: "#dc2626",
};

export default function TriggerStatusPage() {
  const [systemId, setSystemId] = useState("1");
  const [evidencePath, setEvidencePath] = useState("/evidence/sys1");
  const [job, setJob] = useState<JobStatus | null>(null);
  const [triggerError, setTriggerError] = useState<string | null>(null);
  const [isTriggering, setIsTriggering] = useState(false);
  const pollRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (pollRef.current !== null) {
        window.clearInterval(pollRef.current);
      }
    };
  }, []);

  function stopPolling() {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  function startPolling(jobId: number) {
    stopPolling();
    pollRef.current = window.setInterval(async () => {
      try {
        const status = await api.getJobStatus(jobId);
        setJob(status);
        if (status.status === "succeeded" || status.status === "failed") {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, POLL_INTERVAL_MS);
  }

  async function handleRun() {
    setTriggerError(null);
    setIsTriggering(true);
    try {
      const response = await api.triggerIngest(Number(systemId), evidencePath);
      const initialStatus: JobStatus = {
        id: response.job_id,
        status: "queued",
        run_id: response.run_id,
        error_message: null,
      };
      setJob(initialStatus);
      startPolling(response.job_id);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to trigger ingestion.";
      setTriggerError(message);
    } finally {
      setIsTriggering(false);
    }
  }

  return (
    <div className="page">
      <h1>Trigger Ingestion & Job Status</h1>

      <div className="form-row">
        <label>
          System ID
          <input value={systemId} onChange={(e) => setSystemId(e.target.value)} />
        </label>
        <label>
          Evidence path
          <input value={evidencePath} onChange={(e) => setEvidencePath(e.target.value)} />
        </label>
        <button onClick={handleRun} disabled={isTriggering}>
          {isTriggering ? "Starting…" : "Run"}
        </button>
      </div>

      {triggerError && <p className="error-text">Could not start the run: {triggerError}</p>}

      {job && (
        <div className="job-status" data-testid="job-status">
          <span
            className="status-badge"
            style={{ backgroundColor: STATUS_COLOR[job.status] }}
            data-testid="status-badge"
          >
            {STATUS_LABEL[job.status]}
          </span>
          <p>Job #{job.id}</p>
          {job.run_id && <p>Run ID: {job.run_id}</p>}
          {job.status === "failed" && job.error_message && (
            <p className="error-text" data-testid="job-error-message">
              {job.error_message}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
