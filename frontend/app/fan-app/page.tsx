"use client";

import { useState } from "react";
import Navbar from "@/components/shared/Navbar";
import LanguageSelector from "@/components/fan-app/LanguageSelector";
import LowSensoryToggle from "@/components/fan-app/LowSensoryToggle";
import NavigationMap from "@/components/fan-app/NavigationMap";
import ChatAssistant from "@/components/fan-app/ChatAssistant";
import VoiceAssistant from "@/components/fan-app/VoiceAssistant";
import type { Language } from "@/types";

export default function FanAppPage() {
  const [language, setLanguage] = useState<Language>("en");
  const [lowSensoryMode, setLowSensoryMode] = useState(false);

  return (
    <main className="min-h-screen bg-stadium-dark">
      <Navbar />
      <div className="max-w-4xl mx-auto p-6 md:p-8">
        <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-bold text-stadium-text">Welcome, Fan!</h1>
            <p className="text-stadium-muted text-sm mt-1">
              FIFA World Cup 2026 — Your Stadium Companion
            </p>
          </div>
          <div className="flex gap-2">
            <LowSensoryToggle enabled={lowSensoryMode} onChange={setLowSensoryMode} />
            <LanguageSelector value={language} onChange={setLanguage} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <NavigationMap language={language} lowSensoryMode={lowSensoryMode} />
          </div>
          <ChatAssistant language={language} />
          <VoiceAssistant language={language} />
        </div>
      </div>
    </main>
  );
}