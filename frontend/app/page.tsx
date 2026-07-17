import Link from "next/link";
import { Users, Radio, Globe2, Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-stadium-dark flex flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles size={28} className="text-stadium-accent" />
          <h1 className="text-3xl md:text-4xl font-bold text-stadium-text">
            StadiumPulse
          </h1>
        </div>
        <p className="text-stadium-muted text-sm md:text-base mb-10">
          A GenAI-powered ecosystem for FIFA World Cup 2026 stadium operations —
          crowd intelligence, navigation, multi-language assistance, and
          real-time decision support, working together as one system.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/fan-app"
            className="bg-stadium-card border border-white/10 rounded-xl p-6 text-left hover:border-stadium-accent transition-colors group"
          >
            <Users size={24} className="text-stadium-accent mb-3" />
            <h2 className="text-stadium-text font-semibold text-lg mb-1">
              Fan App
            </h2>
            <p className="text-stadium-muted text-sm">
              Navigation, multi-language chat &amp; voice assistant, and
              low-sensory routing — built for fans and volunteers.
            </p>
            <span className="inline-block mt-3 text-stadium-accent text-sm font-medium group-hover:underline">
              Enter Fan App →
            </span>
          </Link>

          <Link
            href="/control-room"
            className="bg-stadium-card border border-white/10 rounded-xl p-6 text-left hover:border-stadium-accent transition-colors group"
          >
            <Radio size={24} className="text-stadium-accent mb-3" />
            <h2 className="text-stadium-text font-semibold text-lg mb-1">
              Control Room
            </h2>
            <p className="text-stadium-muted text-sm">
              Live zone occupancy, auto-detected incidents, and explainable
              AI recommendations — built for staff and organizers.
            </p>
            <span className="inline-block mt-3 text-stadium-accent text-sm font-medium group-hover:underline">
              Enter Control Room →
            </span>
          </Link>
        </div>

        <div className="flex items-center justify-center gap-2 mt-10 text-stadium-muted text-xs">
          <Globe2 size={14} />
          <span>6 languages · Real-time WebSocket updates · Explainable AI</span>
        </div>
      </div>
    </main>
  );
}