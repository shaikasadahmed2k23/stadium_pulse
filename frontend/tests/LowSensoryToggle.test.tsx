import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import LowSensoryToggle from "@/components/fan-app/LowSensoryToggle";

describe("LowSensoryToggle", () => {
  it("renders in disabled state by default", () => {
    render(<LowSensoryToggle enabled={false} onChange={vi.fn()} />);
    const button = screen.getByRole("button", { name: /low-sensory routing mode/i });
    expect(button).toHaveAttribute("aria-pressed", "false");
  });

  it("calls onChange with true when toggled on", () => {
    const onChange = vi.fn();
    render(<LowSensoryToggle enabled={false} onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: /low-sensory routing mode/i }));
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it("calls onChange with false when toggled off", () => {
    const onChange = vi.fn();
    render(<LowSensoryToggle enabled={true} onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: /low-sensory routing mode/i }));
    expect(onChange).toHaveBeenCalledWith(false);
  });
});