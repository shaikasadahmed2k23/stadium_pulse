import type { Metadata } from "next";
import "./globals.css";

export const metadata = {
  title: "StadiumPulse — FIFA World Cup 2026",
  icons: {
    icon: "/favicon.ico",
    apple: "/icon-180.png",
  },
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