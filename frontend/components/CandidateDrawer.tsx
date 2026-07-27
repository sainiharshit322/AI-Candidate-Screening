"use client";

import React, { useState } from "react";
import { X, ExternalLink, Github, FileText, CheckCircle, AlertTriangle, User } from "lucide-react";
import { Candidate, updateCandidateStage, deleteCandidate } from "../lib/api";
import { toast } from "sonner";

interface CandidateDrawerProps {
  candidate: Candidate | null;
  onClose: () => void;
  onCandidateUpdated?: () => void;
}

export const CandidateDrawer: React.FC<CandidateDrawerProps> = ({
  candidate,
  onClose,
  onCandidateUpdated,
}) => {
  const [updating, setUpdating] = useState(false);

  if (!candidate) return null;

  const handleStageChange = async (newStage: string) => {
    setUpdating(true);
    try {
      await updateCandidateStage(candidate.id, newStage);
      toast.success(`Candidate stage updated to '${newStage}'`);
      if (onCandidateUpdated) onCandidateUpdated();
    } catch (e: any) {
      toast.error(`Failed to update stage: ${e.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const getScoreBadge = (score?: number) => {
    if (score === undefined || score === null) return <span className="text-slate-400 font-medium">N/A</span>;
    let color = "bg-slate-100 text-slate-700";
    if (score >= 70) color = "bg-emerald-100 text-emerald-800 border border-emerald-200";
    else if (score >= 40) color = "bg-amber-100 text-amber-800 border border-amber-200";
    else color = "bg-red-100 text-red-800 border border-red-200";
    return <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${color}`}>{score.toFixed(1)}</span>;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-xl bg-white h-full shadow-2xl overflow-y-auto flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-xl font-bold text-slate-900">{candidate.name || "Unnamed Candidate"}</h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 uppercase tracking-wide">
                {candidate.stage}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">{candidate.email}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 flex-1">
          {/* Quick Links & Meta */}
          <div className="grid grid-cols-2 gap-4 text-xs bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div>
              <span className="text-slate-500 block">College</span>
              <span className="font-semibold text-slate-800">{candidate.college || "N/A"}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Branch & CGPA</span>
              <span className="font-semibold text-slate-800">
                {candidate.branch || "N/A"} (CGPA: {candidate.cgpa ?? "N/A"})
              </span>
            </div>
            {candidate.github_url && (
              <div>
                <span className="text-slate-500 block">GitHub Profile</span>
                <a
                  href={candidate.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-600 font-medium inline-flex items-center hover:underline mt-0.5"
                >
                  <Github className="w-3.5 h-3.5 mr-1" /> View GitHub
                </a>
              </div>
            )}
            {candidate.resume_url && (
              <div>
                <span className="text-slate-500 block">Resume Link</span>
                <a
                  href={candidate.resume_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-600 font-medium inline-flex items-center hover:underline mt-0.5"
                >
                  <FileText className="w-3.5 h-3.5 mr-1" /> View Resume
                </a>
              </div>
            )}
          </div>

          {/* Composite Score Breakdown */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-900">Total Composite Score</h3>
              <div>{getScoreBadge(candidate.total_score)}</div>
            </div>

            <div className="space-y-2.5 text-xs">
              <div>
                <div className="flex justify-between text-slate-600 mb-1">
                  <span>AI Fit Score (35%)</span>
                  <span className="font-semibold">{candidate.ai_score ?? 0} / 100</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${Math.min(candidate.ai_score || 0, 100)}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-600 mb-1">
                  <span>GitHub Analysis Score (25%)</span>
                  <span className="font-semibold">{candidate.github_score ?? 0} / 100</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.min(candidate.github_score || 0, 100)}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-600 mb-1">
                  <span>Test Coding Score (25%)</span>
                  <span className="font-semibold">{candidate.test_code ?? 0} / 100</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${Math.min(candidate.test_code || 0, 100)}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-600 mb-1">
                  <span>Test LA Score (10%)</span>
                  <span className="font-semibold">{candidate.test_la ?? 0} / 100</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 rounded-full" style={{ width: `${Math.min(candidate.test_la || 0, 100)}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Reasoning & Strengths / Gaps */}
          {candidate.ai_reasoning && (
            <div className="bg-indigo-50/60 border border-indigo-100 rounded-xl p-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900 mb-1.5">
                AI Match Assessment
              </h4>
              <p className="text-xs text-indigo-950 leading-relaxed">{candidate.ai_reasoning}</p>

              {candidate.ai_strengths && candidate.ai_strengths.length > 0 && (
                <div className="mt-3">
                  <span className="text-[11px] font-semibold text-emerald-800 block mb-1">Key Strengths</span>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.ai_strengths.map((str, i) => (
                      <span key={i} className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-md text-[11px]">
                        ✓ {str}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {candidate.ai_gaps && candidate.ai_gaps.length > 0 && (
                <div className="mt-3">
                  <span className="text-[11px] font-semibold text-amber-800 block mb-1">Potential Gaps</span>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.ai_gaps.map((gap, i) => (
                      <span key={i} className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-md text-[11px]">
                        ⚠ {gap}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* GitHub Summary */}
          {candidate.github_summary && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                GitHub Repository Summary
              </h4>
              <p className="text-xs text-slate-600">{candidate.github_summary}</p>
            </div>
          )}

          {/* Project & Research */}
          <div className="space-y-3">
            {candidate.best_ai_project && (
              <div>
                <h4 className="text-xs font-semibold text-slate-700">Best AI Project</h4>
                <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200 mt-1">
                  {candidate.best_ai_project}
                </p>
              </div>
            )}
            {candidate.research_work && (
              <div>
                <h4 className="text-xs font-semibold text-slate-700">Research Work</h4>
                <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200 mt-1">
                  {candidate.research_work}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer Stage Control & Delete */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={async () => {
                if (confirm(`Are you sure you want to delete ${candidate.name || "this candidate"}?`)) {
                  try {
                    await deleteCandidate(candidate.id);
                    toast.success("Candidate deleted successfully!");
                    onClose();
                    if (onCandidateUpdated) onCandidateUpdated();
                  } catch (e: any) {
                    toast.error(`Delete failed: ${e.message}`);
                  }
                }
              }}
              className="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold rounded-lg border border-red-200 transition"
            >
              Delete Candidate
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-xs font-semibold text-slate-700">Stage:</label>
            <select
              value={candidate.stage}
              disabled={updating}
              onChange={(e) => handleStageChange(e.target.value)}
              className="text-xs font-medium bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="uploaded">Uploaded</option>
              <option value="evaluated">Evaluated</option>
              <option value="test_sent">Test Sent</option>
              <option value="test_done">Test Done</option>
              <option value="interview_scheduled">Interview Scheduled</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};
