export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="w-10 h-10 border-4 border-stadium-accent/30 border-t-stadium-accent rounded-full animate-spin" />
      <p className="text-stadium-muted text-sm">Connecting to live feed…</p>
    </div>
  );
}