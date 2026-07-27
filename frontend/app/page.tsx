"use client";

import React, { useEffect, useState } from "react";
import {
  listCandidates,
  triggerEvaluation,
  sendTestLinks,
  scheduleInterviews,
  clearAllCandidates,
  Candidate,
} from "../lib/api";
import { StatsCards } from "../components/StatsCards";
import { PipelineFunnel } from "../components/PipelineFunnel";
import { CandidateTable } from "../components/CandidateTable";
import { CandidateDrawer } from "../components/CandidateDrawer";
import { toast } from "sonner";
import Link from "next/link";
import { Upload, Play, Mail, Calendar, RefreshCw } from "lucide-react";

export default function DashboardPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const data = await listCandidates();
      setCandidates(data);
    } catch (e: any) {
      toast.error(`Failed to fetch candidates: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleRunEvaluation = async () => {
    setActionLoading("evaluate");
    try {
      // Fetch latest job description ID or mock prompt
      const res = await triggerEvaluation("latest");
      toast.success(`Evaluation triggered! Evaluated ${res.evaluated} candidates.`);
      fetchCandidates();
    } catch (e: any) {
      toast.error(`Evaluation failed: ${e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSendTestLinks = async () => {
    setActionLoading("email");
    try {
      const res = await sendTestLinks(60);
      toast.success(`Test links dispatched to ${res.sent_count} shortlisted candidates!`);
      fetchCandidates();
    } catch (e: any) {
      toast.error(`Failed to send test links: ${e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleScheduleInterviews = async () => {
    setActionLoading("calendar");
    try {
      const res = await scheduleInterviews(70);
      toast.success(`Scheduled ${res.scheduled_count} interview slots for candidates with score >= 70%!`);
      fetchCandidates();
    } catch (e: any) {
      toast.error(`Interview scheduling failed: ${e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header & Quick Action Buttons */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Recruiter Screening Dashboard
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Automated AI resume evaluation, GitHub repo scoring, and Google Meet scheduling.
          </p>
        </div>

        {/* Quick Action Bar */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={fetchCandidates}
            className="p-2 rounded-lg border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          <button
            onClick={async () => {
              if (confirm("Are you sure you want to clear all candidate records? This will delete all candidates from the database.")) {
                try {
                  const res = await clearAllCandidates();
                  toast.success(`Cleared ${res.count} candidates from database!`);
                  fetchCandidates();
                } catch (e: any) {
                  toast.error(`Clear failed: ${e.message}`);
                }
              }
            }}
            className="px-3 py-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold border border-red-200 transition"
          >
            Clear All
          </button>

          <Link
            href="/upload"
            className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition"
          >
            <Upload className="w-4 h-4" />
            <span>Upload CSV</span>
          </Link>

          <button
            onClick={handleRunEvaluation}
            disabled={actionLoading !== null}
            className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition"
          >
            <Play className="w-4 h-4" />
            <span>{actionLoading === "evaluate" ? "Evaluating..." : "Run Evaluation"}</span>
          </button>

          <button
            onClick={handleSendTestLinks}
            disabled={actionLoading !== null}
            className="px-3.5 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition"
          >
            <Mail className="w-4 h-4" />
            <span>{actionLoading === "email" ? "Sending..." : "Send Test Links"}</span>
          </button>

          <button
            onClick={handleScheduleInterviews}
            disabled={actionLoading !== null}
            className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition"
          >
            <Calendar className="w-4 h-4" />
            <span>{actionLoading === "calendar" ? "Scheduling..." : "Schedule Interviews"}</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsCards candidates={candidates} />

      {/* Pipeline Funnel */}
      <PipelineFunnel candidates={candidates} />

      {/* Recent Candidates Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">All Candidate Records</h2>
          <span className="text-xs text-slate-500">
            Showing {candidates.length} total candidates
          </span>
        </div>
        <CandidateTable
          candidates={candidates}
          onSelectCandidate={(c) => setSelectedCandidate(c)}
        />
      </div>

      {/* Candidate Detail Drawer */}
      <CandidateDrawer
        candidate={selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
        onCandidateUpdated={() => {
          fetchCandidates();
          if (selectedCandidate) {
            // refresh selected candidate
          }
        }}
      />
    </div>
  );
}
