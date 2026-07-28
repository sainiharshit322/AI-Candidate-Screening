"use client";

import React, { useState } from "react";
import { Search, ChevronRight, ArrowUpDown, Trash2 } from "lucide-react";
import { Candidate, deleteCandidate } from "../lib/api";
import { toast } from "sonner";

interface CandidateTableProps {
  candidates: Candidate[];
  onSelectCandidate: (candidate: Candidate) => void;
  onCandidateDeleted?: () => void;
}

export const CandidateTable: React.FC<CandidateTableProps> = ({
  candidates,
  onSelectCandidate,
  onCandidateDeleted,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStage, setSelectedStage] = useState("all");
  const [sortField, setSortField] = useState<keyof Candidate>("total_score");
  const [sortAsc, setSortAsc] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const stages = [
    { id: "all", label: "All Candidates" },
    { id: "test_sent", label: "Test Sent" },
    { id: "test_done", label: "Test Done" },
    { id: "shortlisted", label: "Shortlisted (Score ≥ 70%)" },
    { id: "interview_scheduled", label: "Scheduled" },
  ];

  const filtered = candidates.filter((c) => {
    let matchesStage = true;

    if (selectedStage === "shortlisted") {
      // Shortlisted criteria: strictly requires stage to be test_done or interview_scheduled AND total_score >= 70
      matchesStage = ["test_done", "interview_scheduled"].includes(c.stage) && (c.total_score || 0) >= 70;
    } else if (selectedStage === "test_sent") {
      matchesStage = ["test_sent", "test_done", "interview_scheduled"].includes(c.stage);
    } else if (selectedStage === "test_done") {
      matchesStage = ["test_done", "interview_scheduled"].includes(c.stage);
    } else if (selectedStage !== "all") {
      matchesStage = c.stage === selectedStage;
    }

    const term = searchTerm.toLowerCase();
    const matchesSearch =
      !term ||
      (c.name && c.name.toLowerCase().includes(term)) ||
      (c.email && c.email.toLowerCase().includes(term)) ||
      (c.college && c.college.toLowerCase().includes(term));

    return matchesStage && matchesSearch;
  });

  const sorted = [...filtered].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];
    if (valA === undefined || valA === null) return 1;
    if (valB === undefined || valB === null) return -1;
    if (typeof valA === "number" && typeof valB === "number") {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc
      ? String(valA).localeCompare(String(valB))
      : String(valB).localeCompare(String(valA));
  });

  const handleSort = (field: keyof Candidate) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string, name?: string) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete candidate ${name || "record"}?`)) return;
    setDeletingId(id);
    try {
      await deleteCandidate(id);
      toast.success(`Deleted candidate ${name || id}`);
      if (onCandidateDeleted) onCandidateDeleted();
    } catch (err: any) {
      toast.error(`Failed to delete candidate: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const renderScore = (score?: number) => {
    if (score === undefined || score === null) return <span className="text-slate-400 font-mono text-xs">-</span>;
    let cls = "bg-slate-100 text-slate-700";
    if (score >= 70) cls = "bg-emerald-100 text-emerald-800 font-bold border border-emerald-200";
    else if (score >= 50) cls = "bg-amber-100 text-amber-800 font-medium border border-amber-200";
    else cls = "bg-red-100 text-red-800 font-medium border border-red-200";
    return <span className={`px-2 py-0.5 rounded text-xs ${cls}`}>{score.toFixed(1)}</span>;
  };

  const renderStageBadge = (stage: string) => {
    const map: Record<string, string> = {
      uploaded: "bg-slate-100 text-slate-700",
      evaluated: "bg-indigo-100 text-indigo-800",
      test_sent: "bg-amber-100 text-amber-800",
      test_done: "bg-blue-100 text-blue-800",
      interview_scheduled: "bg-emerald-100 text-emerald-800 font-bold",
      rejected: "bg-red-100 text-red-800",
    };
    return (
      <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide ${map[stage] || "bg-slate-100 text-slate-700"}`}>
        {stage.replace("_", " ")}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Controls Bar */}
      <div className="p-4 border-b border-slate-200 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Stage Filter Tabs */}
        <div className="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-lg">
          {stages.map((st) => (
            <button
              key={st.id}
              onClick={() => setSelectedStage(st.id)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                selectedStage === st.id
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-64">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search candidates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700 border-collapse">
          <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Candidate</th>
              <th className="py-3 px-4">College</th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-800" onClick={() => handleSort("cgpa")}>
                <div className="flex items-center space-x-1">
                  <span>CGPA</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-800" onClick={() => handleSort("ai_score")}>
                <div className="flex items-center space-x-1">
                  <span>AI Fit</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-800" onClick={() => handleSort("github_score")}>
                <div className="flex items-center space-x-1">
                  <span>GitHub</span>
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th className="py-3 px-4">Test Code</th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-800" onClick={() => handleSort("total_score")}>
                <div className="flex items-center space-x-1">
                  <span>Total Score</span>
                  <ArrowUpDown className="w-3 h-3 text-indigo-600" />
                </div>
              </th>
              <th className="py-3 px-4">Stage</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-12 text-center text-slate-400 text-sm">
                  {selectedStage === "test_sent"
                    ? "No test sent candidates yet. Candidates appear here after clicking 'Send Test Links'."
                    : selectedStage === "test_done"
                    ? "No test done candidates yet. Candidates appear here after uploading test results."
                    : selectedStage === "shortlisted"
                    ? "No shortlisted candidates yet. Shortlisted candidates appear after test results are uploaded for candidates scoring ≥ 70%."
                    : "No candidates found matching criteria."}
                </td>
              </tr>
            ) : (
              sorted.map((cand) => (
                <tr
                  key={cand.id}
                  onClick={() => onSelectCandidate(cand)}
                  className="hover:bg-indigo-50/40 cursor-pointer transition"
                >
                  <td className="py-3 px-4 font-semibold text-slate-900">
                    <div>{cand.name || "Unnamed"}</div>
                    <div className="text-[11px] font-normal text-slate-400">{cand.email}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-600">{cand.college || "-"}</td>
                  <td className="py-3 px-4 font-mono font-medium">{cand.cgpa ?? "-"}</td>
                  <td className="py-3 px-4">{renderScore(cand.ai_score)}</td>
                  <td className="py-3 px-4">{renderScore(cand.github_score)}</td>
                  <td className="py-3 px-4">{renderScore(cand.test_code)}</td>
                  <td className="py-3 px-4 font-bold">{renderScore(cand.total_score)}</td>
                  <td className="py-3 px-4">{renderStageBadge(cand.stage)}</td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={(e) => handleDelete(e, cand.id, cand.name)}
                        disabled={deletingId === cand.id}
                        className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition"
                        title="Delete candidate"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <button className="text-slate-400 hover:text-indigo-600 p-1">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
