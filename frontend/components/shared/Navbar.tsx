import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-stadium-card border-b border-white/5 px-6 py-4 flex items-center justify-between">
      <Link href="/" className="text-stadium-text font-bold text-lg">
        StadiumPulse
      </Link>
      <div className="flex gap-4 text-sm">
        <Link href="/fan-app" className="text-stadium-muted hover:text-stadium-accent">
          Fan App
        </Link>
        <Link href="/control-room" className="text-stadium-muted hover:text-stadium-accent">
          Control Room
        </Link>
      </div>
    </nav>
  );
}