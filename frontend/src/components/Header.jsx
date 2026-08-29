export default function Header() {
  return (
    <header className="bg-slate-900 border-b border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
            🎯
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">CPIP</h1>
            <p className="text-xs text-slate-400">Career & Placement Intelligence</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-400">Live Dashboard</p>
          <p className="text-xs text-green-400">● Connected</p>
        </div>
      </div>
    </header>
  );
}