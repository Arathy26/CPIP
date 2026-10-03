import { useEffect, useState } from "react";
import cpipApi from "../../services/cpipApi";

/**
 * StudentEvidenceCard — the student adds evidence CPIP cannot read from the
 * resume: skills the parser missed and portfolio links. Saved to the backend;
 * the dashboard reloads so every score uses the new evidence.
 */
export default function StudentEvidenceCard({ studentId, profile, onSaved }) {
  const [open, setOpen] = useState(false);
  const [skillsText, setSkillsText] = useState("");
  const [links, setLinks] = useState({ github_link: "", linkedin_id: "", deployed_demo_link: "", project_readme_link: "" });
  const [status, setStatus] = useState({ type: null, text: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!profile) return;
    setSkillsText((profile.skills || []).join(", "));
    setLinks({
      github_link: profile.portfolio?.github || "",
      linkedin_id: profile.portfolio?.linkedin || "",
      deployed_demo_link: profile.portfolio?.deployed_demo || "",
      project_readme_link: profile.portfolio?.project_readme || "",
    });
  }, [profile]);

  const save = async () => {
    setSaving(true);
    setStatus({ type: null, text: "" });
    try {
      const skills = skillsText.split(",").map((s) => s.trim()).filter(Boolean);
      await cpipApi.updateSkills(studentId, skills);
      const withScheme = (v) => {
        const t = (v || "").trim();
        return t && !/^https?:\/\//i.test(t) ? `https://${t}` : t;
      };
      await cpipApi.updatePortfolioLinks(studentId, {
        github_link: withScheme(links.github_link),
        linkedin_id: withScheme(links.linkedin_id),
        deployed_demo_link: withScheme(links.deployed_demo_link),
        project_readme_link: withScheme(links.project_readme_link),
      });
      setStatus({ type: "ok", text: "Saved. Your scores have been recalculated." });
      onSaved?.();
    } catch (err) {
      setStatus({ type: "error", text: err.message });
    } finally {
      setSaving(false);
    }
  };

  const field = (key, label, placeholder) => (
    <label className="block">
      <span className="text-xs font-semibold text-gray-600">{label}</span>
      <input
        type="text"
        value={links[key]}
        onChange={(e) => setLinks({ ...links, [key]: e.target.value })}
        placeholder={placeholder}
        className="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-purple-500 focus:outline-none"
      />
    </label>
  );

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold text-gray-900">My skills & portfolio evidence</p>
          <p className="text-sm text-gray-500">Add what your resume does not show. Only add real evidence.</p>
        </div>
        <button onClick={() => setOpen(!open)} className="text-sm font-semibold text-purple-600 hover:text-purple-800">
          {open ? "Close" : "Edit"}
        </button>
      </div>

      {open && (
        <div className="mt-4 space-y-3">
          <label className="block">
            <span className="text-xs font-semibold text-gray-600">Skills (comma separated)</span>
            <textarea
              value={skillsText}
              onChange={(e) => setSkillsText(e.target.value)}
              rows={2}
              className="mt-1 w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-purple-500 focus:outline-none"
            />
          </label>
          <div className="grid grid-cols-2 gap-3">
            {field("github_link", "GitHub", "https://github.com/you/project")}
            {field("linkedin_id", "LinkedIn", "https://linkedin.com/in/you")}
            {field("deployed_demo_link", "Deployed demo", "https://your-app.onrender.com")}
            {field("project_readme_link", "Project README", "https://github.com/you/project#readme")}
          </div>
          <div className="flex items-center gap-3">
            <button onClick={save} disabled={saving}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-semibold hover:bg-purple-700 disabled:opacity-50">
              {saving ? "Saving..." : "Save"}
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
