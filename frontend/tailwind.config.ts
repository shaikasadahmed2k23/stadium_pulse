import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // FIFA World Cup 2026 inspired palette — avoid generic AI blue/purple defaults
stadium: {
          dark: "#0B1120",      // deep navy background (control room feel)
          card: "#141B2D",
          accent: "#00C896",    // pitch green
          warning: "#F59E0B",
          critical: "#F87171",     // lightened from #EF4444 for WCAG AA contrast on dark bg
          text: "#E2E8F0",
          muted: "#94A3B8",     // lightened from #64748B for WCAG AA contrast on dark bg
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;