import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { act, render, screen, fireEvent } from "@testing-library/react";
import TriggerStatusPage from "../TriggerStatusPage";
import { api } from "../../api/client";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return {
    ...actual,
    api: {
      triggerIngest: vi.fn(),
      getJobStatus: vi.fn(),
    },
  };
});

async function flush() {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(0);
  });
}

async function advance(ms: number) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

describe("TriggerStatusPage", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("triggers a job and shows queued status immediately", async () => {
    vi.mocked(api.triggerIngest).mockResolvedValue({ job_id: 42, run_id: "run-abc", status: "queued" });

    render(<TriggerStatusPage />);
    fireEvent.click(screen.getByText("Run"));
    await flush();

    expect(screen.getByTestId("job-status")).toBeInTheDocument();
    expect(screen.getByTestId("status-badge")).toHaveTextContent("Queued");
    expect(screen.getByText("Job #42")).toBeInTheDocument();
  });

  it("polls and updates status through running to succeeded without a page reload", async () => {
    vi.mocked(api.triggerIngest).mockResolvedValue({ job_id: 1, run_id: "run-1", status: "queued" });
    vi.mocked(api.getJobStatus)
      .mockResolvedValueOnce({ id: 1, status: "running", run_id: "run-1", error_message: null })
      .mockResolvedValueOnce({ id: 1, status: "succeeded", run_id: "run-1", error_message: null });

    render(<TriggerStatusPage />);
    fireEvent.click(screen.getByText("Run"));
    await flush();

    await advance(3000);
    expect(screen.getByTestId("status-badge")).toHaveTextContent("Running");

    await advance(3000);
    expect(screen.getByTestId("status-badge")).toHaveTextContent("Succeeded");

    expect(api.getJobStatus).toHaveBeenCalledTimes(2);
  });

  it("shows the error_message when a job fails", async () => {
    vi.mocked(api.triggerIngest).mockResolvedValue({ job_id: 2, run_id: "run-2", status: "queued" });
    vi.mocked(api.getJobStatus).mockResolvedValueOnce({
      id: 2,
      status: "failed",
      run_id: "run-2",
      error_message: "validator found 1 violation(s)",
    });

    render(<TriggerStatusPage />);
    fireEvent.click(screen.getByText("Run"));
    await flush();

    await advance(3000);

    expect(screen.getByTestId("job-error-message")).toHaveTextContent("validator found 1 violation(s)");
    expect(screen.getByTestId("status-badge")).toHaveTextContent("Failed");
  });

  it("stops polling once a terminal status is reached", async () => {
    vi.mocked(api.triggerIngest).mockResolvedValue({ job_id: 3, run_id: "run-3", status: "queued" });
    vi.mocked(api.getJobStatus).mockResolvedValue({
      id: 3,
      status: "succeeded",
      run_id: "run-3",
      error_message: null,
    });

    render(<TriggerStatusPage />);
    fireEvent.click(screen.getByText("Run"));
    await flush();

    await advance(3000);
    expect(screen.getByTestId("status-badge")).toHaveTextContent("Succeeded");

    await advance(9000);
    expect(api.getJobStatus).toHaveBeenCalledTimes(1);
  });
});
