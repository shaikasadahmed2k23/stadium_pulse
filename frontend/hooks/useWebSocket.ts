/**
 * React hook wrapping ControlRoomSocket — gives components live
 * control room state + connection status with automatic cleanup.
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { ControlRoomSocket } from "@/lib/websocket-client";
import type { ControlRoomState } from "@/types";

export function useControlRoomSocket() {
  const [state, setState] = useState<ControlRoomState | null>(null);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<ControlRoomSocket | null>(null);

  useEffect(() => {
    const socket = new ControlRoomSocket(setState, setConnected);
    socketRef.current = socket;
    socket.connect();

    return () => {
      socket.disconnect();
    };
  }, []);

  return { state, connected };
}