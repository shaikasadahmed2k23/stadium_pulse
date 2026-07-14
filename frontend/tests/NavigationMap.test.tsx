import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import NavigationMap from "@/components/fan-app/NavigationMap";
import { apiClient } from "@/lib/api-client";

vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getNavigationRoute: vi.fn(),
  },
}));

describe("NavigationMap", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the search input and button", () => {
    render(<NavigationMap language="en" lowSensoryMode={false} />);
    expect(screen.getByLabelText("Navigation query")).toBeInTheDocument();
    expect(screen.getByText("Go")).toBeInTheDocument();
  });

  it("displays route steps after a successful search", async () => {
    (apiClient.getNavigationRoute as any).mockResolvedValue({
      route: [
        { instruction: "Enter through Gate 1", zone: "gate_1", estimated_time_seconds: 30, congestion_level: "normal" },
        { instruction: "Arrive at Section 101", zone: "section_101", estimated_time_seconds: 20, congestion_level: "normal" },
      ],
      total_estimated_time_seconds: 50,
      route_avoids_congestion: true,
    });

    render(<NavigationMap language="en" lowSensoryMode={false} />);
    const input = screen.getByLabelText("Navigation query");

    fireEvent.change(input, { target: { value: "section 101" } });
    fireEvent.click(screen.getByText("Go"));

    await waitFor(() => {
      expect(screen.getByText("Enter through Gate 1")).toBeInTheDocument();
      expect(screen.getByText("Arrive at Section 101")).toBeInTheDocument();
    });
  });

  it("shows an error message when route lookup fails", async () => {
    (apiClient.getNavigationRoute as any).mockRejectedValue(new Error("Not found"));

    render(<NavigationMap language="en" lowSensoryMode={false} />);
    const input = screen.getByLabelText("Navigation query");

    fireEvent.change(input, { target: { value: "unknown place" } });
    fireEvent.click(screen.getByText("Go"));

    await waitFor(() => {
      expect(screen.getByText(/Couldn't find a route/i)).toBeInTheDocument();
    });
  });

  it("passes low_sensory_mode flag correctly to the API", async () => {
    (apiClient.getNavigationRoute as any).mockResolvedValue({
      route: [],
      total_estimated_time_seconds: 0,
      route_avoids_congestion: true,
    });

    render(<NavigationMap language="en" lowSensoryMode={true} />);
    const input = screen.getByLabelText("Navigation query");

    fireEvent.change(input, { target: { value: "restroom" } });
    fireEvent.click(screen.getByText("Go"));

    await waitFor(() => {
      expect(apiClient.getNavigationRoute).toHaveBeenCalledWith(
        expect.objectContaining({ low_sensory_mode: true })
      );
    });
  });

  it("does not search with an empty query", () => {
    render(<NavigationMap language="en" lowSensoryMode={false} />);
    fireEvent.click(screen.getByText("Go"));
    expect(apiClient.getNavigationRoute).not.toHaveBeenCalled();
  });
});