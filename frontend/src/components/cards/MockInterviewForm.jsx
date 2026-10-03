import { useState } from "react";
import cpipApi from "../../services/cpipApi";

/**
 * MockInterviewForm — for a MENTOR / placement officer to record the result
 * of a mock interview. Leave a dimension empty if it was not tested.
 * (No login/role check yet — role-based access is a Stage 5 item.)
 */
const DIMENSIONS = [
  ["aptitude_score", "Aptitude"],
  ["technical_score", "Technical"],
  ["communication_score", "Communication"],
  ["project_explanation_score", "Project explanation"],
];

export default function MockInterviewForm({ studentId, onSaved }) {
  const [open, setOpen] = useState(false);
  const [assessedBy, setAssessedBy] = useState("");
  const [scores, setScores] = useState({});
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState({ type: null, text: "" });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    setStatus({ type: null, text: "" });
    const payload = { student_id: Number(studentId), assessed_by: assessedBy.trim(), notes: notes.trim() || null };
    for (const [key] of DIMENSIONS) {
      const raw = scores[key];
      if (raw !== undefined && raw !== "") payload[key] = Number(raw);
    }
    if (!payload.assessed_by) return setStatus({ type: "error", text: "Enter the assessor's name." });
    setSaving(true);
    try {
      await cpipApi.recordInterviewAssessment(payload);
      setStatus({ type: "ok", text: "Mock interview recorded." });
      setScores({});
      setNotes("");
      onSaved?.();
    } catch (err) {
      setStatus({ type: "error", text: err.message });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-dashed border-blue-200 shadow-sm p-6 mb-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold text-gray-900">Mentor: record a mock interview</p>
          <p className="text-sm text-gray-500">Interview readiness comes only from these human assessments.</p>
        </div>
        <button onClick={() => setOpen(!open)} className="text-sm font-semibold text-blue-600 hover:text-blue-800">
          {open ? "Close" : "Record"}
        </button>
      </div>

      {open && (
        <div className="mt-4 space-y-3">
          <label className="block">
            <span className="text-xs font-semibold text-gray-600">Assessed by</span>
            <input type="text" value={assessedBy} onChange={(e) => setAssessedBy(e.target.value)}
              placeholder="Mentor name"
              className="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-blue-500 focus:outline-none" />
          </label>
          <div className="grid grid-cols-4 gap-3">
            {DIMENSIONS.map(([key, label]) => (
              <label key={key} className="block">
                <span className="text-xs font-semibold text-gray-600">{label} (0-100)</span>
                <input type="number" min="0" max="100" value={scores[key] ?? ""}
                  onChange={(e) => setScores({ ...scores, [key]: e.target.value })}
                  placeholder="not tested"
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-blue-500 focus:outline-none" />
              </label>
            ))}
          </div>
          <label className="block">
            <span className="text-xs font-semibold text-gray-600">Notes</span>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2}
              placeholder="e.g. Strong on project architecture, weak on SQL joins"
              className="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-blue-500 focus:outline-none" />
          </label>
          <div className="flex items-center gap-3">
            <button onClick={save} disabled={saving}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50">
              {saving ? "Saving..." : "Save assessment"}
            </button>
            {status.text && (
              <span className={`text-sm ${status.type === "error" ? "text-red-600" : "text-green-700"}`}>{status.text}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
