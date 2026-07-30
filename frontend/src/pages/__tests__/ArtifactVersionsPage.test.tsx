import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { act, render, screen } from "@testing-library/react";
import { fireEvent } from "@testing-library/react";
import ArtifactVersionsPage from "../ArtifactVersionsPage";
import { api } from "../../api/client";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return { ...actual, api: { listArtifactVersions: vi.fn() } };
});

async function flush() {
  await act(async () => {
    await Promise.resolve();
  });
}

describe("ArtifactVersionsPage", () => {
  beforeEach(() => vi.clearAllMocks());
  afterEach(() => vi.unstubAllEnvs());

  it("lists all artifact versions with commit, phase, and status", async () => {
    vi.mocked(api.listArtifactVersions).mockResolvedValue([
      { id: 1, commit_sha: "abc1234567890", phase: "as-is", pr_number: 3, approval_status: "approved" },
      { id: 2, commit_sha: "def0987654321", phase: "as-is", pr_number: 4, approval_status: "pending" },
    ]);

    render(<ArtifactVersionsPage />);
    fireEvent.click(screen.getByText("Load"));
    await flush();

    const rows = screen.getAllByTestId("version-row");
    expect(rows).toHaveLength(2);
    expect(rows[0]).toHaveTextContent("abc1234");
    expect(rows[0]).toHaveTextContent("as-is");
    expect(rows[0]).toHaveTextContent("approved");
    expect(rows[1]).toHaveTextContent("pending");
  });

  it("links to the actual GitHub PR", async () => {
    vi.stubEnv("VITE_GITHUB_REPO", "acme/model-repo");
    vi.mocked(api.listArtifactVersions).mockResolvedValue([
      { id: 1, commit_sha: "abc1234567890", phase: "as-is", pr_number: 7, approval_status: "approved" },
    ]);

    render(<ArtifactVersionsPage />);
    fireEvent.click(screen.getByText("Load"));
    await flush();

    const link = screen.getByText("#7");
    expect(link.tagName).toBe("A");
    expect(link).toHaveAttribute("href", "https://github.com/acme/model-repo/pull/7");
  });

  it("shows a dash when there is no PR yet", async () => {
    vi.mocked(api.listArtifactVersions).mockResolvedValue([
      { id: 1, commit_sha: "abc1234567890", phase: "as-is", pr_number: null, approval_status: "pending" },
    ]);

    render(<ArtifactVersionsPage />);
    fireEvent.click(screen.getByText("Load"));
    await flush();

    expect(screen.getByTestId("version-row")).toHaveTextContent("—");
  });

  it("shows an empty state when there are no versions", async () => {
    vi.mocked(api.listArtifactVersions).mockResolvedValue([]);

    render(<ArtifactVersionsPage />);
    fireEvent.click(screen.getByText("Load"));
    await flush();

    expect(screen.getByText("No artifact versions for this system.")).toBeInTheDocument();
  });

  it("shows an error message when loading fails", async () => {
    vi.mocked(api.listArtifactVersions).mockRejectedValue(new Error("server error"));

    render(<ArtifactVersionsPage />);
    fireEvent.click(screen.getByText("Load"));
    await flush();

    expect(screen.getByText(/server error|Failed to load/)).toBeInTheDocument();
  });
});
