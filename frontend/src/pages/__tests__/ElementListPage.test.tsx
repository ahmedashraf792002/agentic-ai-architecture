import { describe, it, expect, vi, beforeEach } from "vitest";
import { act, render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ElementListPage from "../ElementListPage";
import { api } from "../../api/client";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return { ...actual, api: { listElements: vi.fn() } };
});

async function flush() {
  await act(async () => {
    await Promise.resolve();
  });
}

describe("ElementListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("groups elements by layer matching model_element_index data", async () => {
    vi.mocked(api.listElements).mockResolvedValue([
      { id: "app-1", layer: "application", archimate_type: "Application Service", name: "Payment Service" },
      { id: "biz-1", layer: "business", archimate_type: "Business Process", name: "Checkout" },
      { id: "app-2", layer: "application", archimate_type: "Data Object", name: "Order" },
    ]);

    render(
      <MemoryRouter>
        <ElementListPage />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByText("Load"));
    await flush();

    const appGroup = screen.getByTestId("layer-group-application");
    expect(appGroup).toHaveTextContent("Payment Service");
    expect(appGroup).toHaveTextContent("Order");

    const bizGroup = screen.getByTestId("layer-group-business");
    expect(bizGroup).toHaveTextContent("Checkout");
  });

  it("links each element to its detail page", async () => {
    vi.mocked(api.listElements).mockResolvedValue([
      { id: "app-1", layer: "application", archimate_type: "Application Service", name: "Payment Service" },
    ]);

    render(
      <MemoryRouter>
        <ElementListPage />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByText("Load"));
    await flush();

    const link = screen.getByText("Payment Service").closest("a");
    expect(link).toHaveAttribute("href", "/elements/app-1");
  });

  it("shows an error message when loading fails", async () => {
    vi.mocked(api.listElements).mockRejectedValue(new Error("network down"));

    render(
      <MemoryRouter>
        <ElementListPage />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByText("Load"));
    await flush();

    expect(screen.getByText(/network down|Failed to load/)).toBeInTheDocument();
  });
});
