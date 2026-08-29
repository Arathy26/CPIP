/**
 * ActionPlanCard — matches the mockup's urgency-colored action step cards
 * (red = urgent, amber = soon).
 *
 * SAME PROPS as before: { title, duration, ctaText, color }.
 * useCPIP.js already sends color as "red" or "amber" — this maps those
 * to full styling. Any other color value falls back to the amber style.
 */
const COLOR_STYLES = {
  red: {
    border: 'border-red-400',
    bg: 'bg-gradient-to-r from-red-50 to-orange-50',
    pill: 'bg-red-500 text-white',
    button: 'bg-gradient-to-r from-red-500 to-orange-500 text-white hover:opacity-90',
  },
  amber: {
    border: 'border-amber-400',
    bg: 'bg-white',
    pill: 'bg-amber-500 text-white',
    button: 'border-2 border-amber-400 text-amber-700 hover:bg-amber-50',
  },
};

export default function ActionPlanCard({ title, duration, ctaText, color }) {
  const style = COLOR_STYLES[color] || COLOR_STYLES.amber;

  return (
    <div className={`rounded-2xl p-6 shadow-sm border-l-4 ${style.border} ${style.bg} mb-4`}>
      <div className="flex items-center justify-between gap-4">
        <p className="text-lg font-bold text-gray-900">{title}</p>
        {duration && duration !== '—' && (
          <span className={`px-3 py-1.5 rounded-lg text-sm font-semibold shrink-0 ${style.pill}`}>
            {duration}
          </span>
        )}
      </div>
      <button
        type="button"
        className={`mt-4 w-full py-3 rounded-xl font-semibold transition ${style.button}`}
      >
        {ctaText}
      </button>
    </div>
  );
}
