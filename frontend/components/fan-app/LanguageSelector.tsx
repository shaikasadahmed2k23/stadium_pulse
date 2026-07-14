"use client";

import type { Language } from "@/types";

const LANGUAGES: { code: Language; label: string }[] = [
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "pt", label: "Português" },
  { code: "ar", label: "العربية" },
  { code: "hi", label: "हिन्दी" },
];

export default function LanguageSelector({
  value,
  onChange,
}: {
  value: Language;
  onChange: (lang: Language) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as Language)}
      aria-label="Select language"
      className="bg-stadium-card border border-white/10 text-stadium-text text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-stadium-accent"
    >
      {LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.label}
        </option>
      ))}
    </select>
  );
}