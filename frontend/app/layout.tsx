import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StadiumPulse — FIFA World Cup 2026 Operations",
  description: "GenAI-powered smart stadium ecosystem for tournament operations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}