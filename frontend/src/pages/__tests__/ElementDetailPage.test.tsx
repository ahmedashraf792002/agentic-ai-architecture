import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { act, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import ElementDetailPage from "../ElementDetailPage";
import { api } from "../../api/client";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return { ...actual, api: { getElement: vi.fn() } };
});

async function flush() {
  await act(async () => {
    await Promise.resolve();
  });
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/elements/:elementId" element={<ElementDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ElementDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());
  afterEach(() => vi.unstubAllEnvs());

  it("shows documentation and the actual evidence citation text, not a summary", async () => {
    vi.mocked(api.getElement).mockResolvedValue({
      id: "app-1",
      layer: "application",
      archimate_type: "Application Service",
      name: "Payment Service",
      documentation: "Handles payment authorization.",
      confidence: "observed",
      current_commit: "abc123",
      evidence: [
        { source_type: "code", locator: "src/payments/service.py", excerpt: "class PaymentService:" },
      ],
      relationships: [],
    });

    renderAt("/elements/app-1");
    await flush();

    expect(screen.getByTestId("documentation")).toHaveTextContent("Handles payment authorization.");
    expect(screen.getByTestId("evidence-list")).toHaveTextContent("class PaymentService:");
  });

  it("links a file-path evidence citation to the GitHub blob URL using the element's commit", async () => {
    vi.stubEnv("VITE_GITHUB_REPO", "acme/model-repo");
    vi.mocked(api.getElement).mockResolvedValue({
      id: "app-1",
      layer: "application",
      archimate_type: "Application Service",
      name: "Payment Service",
      documentation: "x",
      confidence: "observed",
      current_commit: "abc123",
      evidence: [{ source_type: "code", locator: "src/payments/service.py" }],
      relationships: [],
    });

    renderAt("/elements/app-1");
    await flush();

    const link = screen.getByText("src/payments/service.py");
    expect(link.tagName).toBe("A");
    expect(link).toHaveAttribute(
      "href",
      expect.stringContaining("/blob/abc123/src/payments/service.py"),
    );
  });

  it("renders relationships as clickable links to the related element", async () => {
    vi.mocked(api.getElement).mockResolvedValue({
      id: "app-1",
      layer: "application",
      archimate_type: "Application Service",
      name: "Payment Service",
      documentation: "x",
      confidence: "observed",
      evidence: [{ source_type: "code", locator: "x.py" }],
      relationships: [{ target_id: "biz-checkout", type: "Serving" }],
    });

    renderAt("/elements/app-1");
    await flush();

    const relLink = screen.getByText("biz-checkout");
    expect(relLink.tagName).toBe("A");
    expect(relLink).toHaveAttribute("href", "/elements/biz-checkout");
  });

  it("shows an error message when the element fails to load", async () => {
    vi.mocked(api.getElement).mockRejectedValue(new Error("not found"));

    renderAt("/elements/does-not-exist");
    await flush();

    expect(screen.getByText(/not found|Failed to load/)).toBeInTheDocument();
  });
});
