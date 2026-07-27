"use client";

import React, { useEffect, useState } from "react";
import { listCandidates, clearAllCandidates, Candidate } from "../../lib/api";
import { CandidateTable } from "../../components/CandidateTable";
import { CandidateDrawer } from "../../components/CandidateDrawer";
import { toast } from "sonner";
import { Users, RefreshCw } from "lucide-react";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const data = await listCandidates();
      setCandidates(data);
    } catch (e: any) {
      toast.error(`Failed to load candidates: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center space-x-2">
            <Users className="w-6 h-6 text-indigo-600" />
            <span>Candidate Management & Pipeline</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Filter, sort, inspect AI fit reasoning, and manage pipeline stages for all applicants.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchCandidates}
            className="p-2 rounded-lg border border-slate-300 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          
          <button
            onClick={async () => {
              if (confirm("Are you sure you want to clear all candidate records?")) {
                try {
                  const res = await clearAllCandidates();
                  toast.success(`Cleared ${res.count} candidates!`);
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
        </div>
      </div>

      {/* Candidate Table */}
      <CandidateTable
        candidates={candidates}
        onSelectCandidate={(cand) => setSelectedCandidate(cand)}
      />

      {/* Candidate Detail Drawer */}
      <CandidateDrawer
        candidate={selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
        onCandidateUpdated={fetchCandidates}
      />
    </div>
  );
}
