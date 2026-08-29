export default function MatchCard({ title, fit, skills }) {
  const fitColor = fit >= 70 ? 'bg-green-600' : fit >= 50 ? 'bg-blue-600' : 'bg-amber-600';
  const fitLabel = fit >= 70 ? 'Strong match' : fit >= 50 ? 'Good match' : 'Fair match';

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <p className="text-white font-semibold text-sm">{title}</p>
        </div>
        <div className={`${fitColor} text-white px-3 py-1 rounded text-xs font-bold whitespace-nowrap ml-2`}>
          {fit}%
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {skills.map((skill) => (
          <span
            key={skill}
            className="bg-slate-700 text-slate-300 px-2 py-1 rounded text-xs font-medium"
          >
            {skill}
          </span>
        ))}
      </div>

      <button className="w-full bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold py-2 rounded transition">
        View details →
      </button>
    </div>
  );
}