/**
 * WebSocket client wrapper for the Control Room live feed. Handles
 * reconnection so a dropped connection (common on flaky demo Wi-Fi)
 * doesn't kill the dashboard permanently.
 */
import type { ControlRoomState } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type StateHandler = (state: ControlRoomState) => void;
type StatusHandler = (connected: boolean) => void;

export class ControlRoomSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private shouldReconnect = true;

  constructor(
    private onState: StateHandler,
    private onStatusChange?: StatusHandler
  ) {}

  connect(): void {
    this.shouldReconnect = true;
    this.ws = new WebSocket(`${WS_URL}/ws/control-room`);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.onStatusChange?.(true);
    };

    this.ws.onmessage = (event) => {
      try {
        const state: ControlRoomState = JSON.parse(event.data);
        this.onState(state);
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    this.ws.onclose = () => {
      this.onStatusChange?.(false);
      if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts += 1;
        setTimeout(() => this.connect(), this.reconnectDelay);
      }
    };

    this.ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.ws?.close();
    this.ws = null;
  }
}