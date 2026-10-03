import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import cpipApi from "../services/cpipApi";

/**
 * Loads everything the candidate dashboard shows.
 *
 * Rule: a value the backend could not measure stays `null` ("not assessed")
 * and is shown as "—". It is NEVER turned into 0, because 0 would tell the
 * student they scored zero when the truth is "no data yet".
 *
 * `refreshKey` — bump it after a save to reload the dashboard.
 */
const EMPTY = {
  readiness: null,
  calculation: null,
  scoresMissing: [],
  targetRole: null,
  jobs: 0,
  skillsHave: [],
  skillsMissing: [],
  gapScore: null,
  skillGapMessage: null,
  basedOnPostings: null,
  actionPlans: [],
  jobMatches: [],
  notifications: [],
  unreadNotificationCount: 0,
  interviewScore: null,
  portfolioScore: null,
  resumeScore: null,
  topMissingSkill: null,
  profile: null,
  loading: true,
  error: null,
};

const value = (res) => (res.status === "fulfilled" ? res.value : null);

export function useCPIP(refreshKey = 0) {
  const { studentId } = useParams();
  const [state, setState] = useState(EMPTY);

  useEffect(() => {
    if (!studentId) {
      setState({ ...EMPTY, loading: false, error: "No studentId found in the URL." });
      return;
    }

    let cancelled = false;

    async function load() {
      const results = await Promise.allSettled([
        cpipApi.getSkillGap(studentId),
        cpipApi.getJobMatch(studentId),
        cpipApi.getTrainingPlan(studentId),
        cpipApi.getNotifications(studentId),
        cpipApi.getReadinessScores(studentId),
        cpipApi.getCandidateProfile(studentId),
      ]);
      if (cancelled) return;

      const [skillGap, jobMatch, training, notificationsData, readinessData, profileData] =
        results.map(value);

      // Skill gap vs target role (recruiter postings)
      const gap = skillGap?.gap_analysis ?? null;
      const skillsMissing = gap?.missing_skills ?? [];
      const firstMissing = skillsMissing[0];
      const topMissingSkill =
        typeof firstMissing === "string" ? firstMissing : firstMissing?.skill ?? null;

      // Job matches (recruiter postings only)
      const jobAnalysis = jobMatch?.job_match_analysis ?? null;
      const jobMatches = jobAnalysis?.all_matches ?? [];

      // Training plan — every action comes from a real gap
      const plan = training?.training_plan ?? null;
      const actionPlans = (plan?.training_actions ?? []).map((a) => ({
        rank: a.rank,
        category: a.category,
        title: a.action,
        reason: a.reason,
      }));

      setState({
        readiness: readinessData?.overall_readiness ?? null,
        calculation: readinessData?.calculation ?? null,
        scoresMissing: readinessData?.scores_missing ?? [],
        targetRole: readinessData?.target_role ?? gap?.target_role ?? null,
        jobs: jobMatches.length,
        skillsHave: gap?.matched_skills ?? [],
        skillsMissing,
        gapScore: gap?.gap_score ?? null,
        skillGapMessage: gap?.message ?? null,
        basedOnPostings: gap?.job_postings_analyzed || null,
        actionPlans,
        jobMatches,
        notifications: notificationsData?.notifications ?? [],
        unreadNotificationCount: notificationsData?.unread_count ?? 0,
        interviewScore: readinessData?.interview_readiness_score ?? null,
        portfolioScore: readinessData?.portfolio_score ?? null,
        resumeScore: readinessData?.resume_score ?? null,
        topMissingSkill,
        profile: profileData?.candidate_profile ?? null,
        loading: false,
        error:
          !readinessData && !skillGap && !jobMatch
            ? "Could not load candidate data. Is the backend running?"
            : null,
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [studentId, refreshKey]);

  return state;
}
