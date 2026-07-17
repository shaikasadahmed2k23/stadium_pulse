import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ChatAssistant from "@/components/fan-app/ChatAssistant";
import { apiClient } from "@/lib/api-client";

vi.mock("@/lib/api-client", () => ({
  apiClient: {
    sendChatMessage: vi.fn(),
  },
}));

describe("ChatAssistant", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the welcome message on load", () => {
    render(<ChatAssistant language="en" />);
    expect(screen.getByText(/Welcome to FIFA World Cup 2026/i)).toBeInTheDocument();
  });

  it("sends a message and displays the assistant reply", async () => {
    (apiClient.sendChatMessage as any).mockResolvedValue({
      reply: "Restrooms are near Concourse A.",
      detected_intent: "general",
      routed_to_wayfinding: false,
      session_id: "test-session",
    });

    render(<ChatAssistant language="en" />);
    const input = screen.getByLabelText("Chat message");

    fireEvent.change(input, { target: { value: "Where is the restroom?" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(screen.getByText("Restrooms are near Concourse A.")).toBeInTheDocument();
    });

    expect(apiClient.sendChatMessage).toHaveBeenCalledWith(
      expect.objectContaining({ message: "Where is the restroom?", language: "en" })
    );
  });

  it("shows an error message when the API call fails", async () => {
    (apiClient.sendChatMessage as any).mockRejectedValue(new Error("Network error"));

    render(<ChatAssistant language="en" />);
    const input = screen.getByLabelText("Chat message");

    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(screen.getByText(/Sorry, something went wrong/i)).toBeInTheDocument();
    });
  });

  it("does not send empty messages", () => {
    render(<ChatAssistant language="en" />);
    const input = screen.getByLabelText("Chat message");

    fireEvent.keyDown(input, { key: "Enter" });

    expect(apiClient.sendChatMessage).not.toHaveBeenCalled();
  });
});