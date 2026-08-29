import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import cpipApi from "../services/cpipApi";

export function useCPIP(searchedRole = null, preferredLocation = null) {
  const { studentId } = useParams();

  const [state, setState] = useState({
    readiness: 0,
    jobs: 0,
    skillsHave: [],
    skillsMissing: [],
    gapScore: 0,
    skillGapSupported: true,
    skillGapMessage: null,
    basedOnPostings: null,
    resumeQuality: null,
    actionPlans: [],
    jobMatches: [],
    notifications: [],
    unreadNotificationCount: 0,
    interviewScore: 0,
    portfolioScore: 0,
    resumeScore: 0,
    topMissingSkill: null,
    needsLocation: false,  // NEW: true when backend needs location
    loading: true,
    error: null,
  });

  useEffect(() => {
    if (!studentId) {
      setState((s) => ({
        ...s,
        loading: false,
        error: "No studentId found in the URL.",
      }));
      return;
    }

    let cancelled = false;

    async function load() {
      const [skillGapRes, jobMatchRes, trainingRes, notificationsRes, readinessRes] =
        await Promise.allSettled([
          cpipApi.getSkillGap(studentId),
          cpipApi.getJobMatch(studentId, preferredLocation), // ← pass location
          cpipApi.getTrainingPlan(studentId),
          cpipApi.getNotifications(studentId),
          cpipApi.getReadinessScores(studentId),
        ]);

      if (cancelled) return;

      const skillGap = skillGapRes.status === "fulfilled" ? skillGapRes.value : null;
      const jobMatch = jobMatchRes.status === "fulfilled" ? jobMatchRes.value : null;
      const training = trainingRes.status === "fulfilled" ? trainingRes.value : null;
      const readinessData = readinessRes.status === "fulfilled" ? readinessRes.value : null;

      const skillGapSupported = skillGap?.supported !== false;
      const gapAnalysis = skillGap?.gap_analysis ?? null;

      const gapScore = skillGapSupported ? gapAnalysis?.gap_score ?? 0 : null;
      const skillsHave = skillGapSupported ? gapAnalysis?.matched_skills ?? [] : [];
      const skillsMissing = skillGapSupported ? gapAnalysis?.missing_skills ?? [] : [];
      const skillGapMessage = skillGap?.message ?? null;
      const basedOnPostings = gapAnalysis?.based_on_postings ?? null;
      const resumeQuality = gapAnalysis?.resume_quality ?? null;
      const rawTop = skillsMissing[0];
      const topMissingSkill =
  gapAnalysis?.detailed_missing?.[0]?.skill ??
  (typeof rawTop === 'string' ? rawTop : rawTop?.skill) ??
  null;
      const jobMatchAnalysis = jobMatch?.job_match_analysis ?? null;
      const allJobMatches = jobMatchAnalysis?.all_matches ?? [];
      const suitableJobs = jobMatchAnalysis?.suitable_jobs ?? [];
      const jobs = suitableJobs.length;

      // Check if backend is asking for location
      const needsLocation = jobMatchAnalysis?.needs_location === true;

      const trainingData = training?.training_plan ?? training;
      const actionPlans = (
        trainingData?.training_actions ??
        trainingData?.priority_actions ??
        []
      ).map((action) => {
        const isString = typeof action === "string";
        return {
          title: isString
            ? action
            : action.action ?? action.skill ?? action.title ?? "Recommended action",
          duration: isString
            ? "14"
            : action.estimated_weeks
            ? String(action.estimated_weeks * 7)
            : "14",
          ctaText: isString ? "Start →" : action.cta_text ?? "Start →",
          color: isString
            ? "amber"
            : action.urgency === "urgent"
            ? "red"
            : "amber",
        };
      });

      const readiness = gapScore ?? 0;

      const notificationsData =
        notificationsRes.status === "fulfilled" ? notificationsRes.value : null;
      const notifications = notificationsData?.notifications ?? [];
      const unreadNotificationCount = notificationsData?.unread_count ?? 0;

      const interviewScore = readinessData?.interview_readiness_score ?? 0;
      const portfolioScore = readinessData?.portfolio_score ?? 0;
      const resumeScore = readinessData?.resume_score ?? 0;

      setState({
        readiness,
        jobs,
        skillsHave,
        skillsMissing,
        gapScore,
        skillGapSupported,
        skillGapMessage,
        basedOnPostings,
        resumeQuality,
        actionPlans,
        jobMatches: allJobMatches,
        notifications,
        unreadNotificationCount,
        interviewScore,
        portfolioScore,
        resumeScore,
        topMissingSkill,
        needsLocation,
        loading: false,
        error:
          !skillGap && !jobMatch && !training
            ? "Could not load any candidate data."
            : null,
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [studentId, searchedRole, preferredLocation]); // ← re-run when location changes

  return state;
}