"use client";

import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";
import { Candidate } from "../lib/api";

interface PipelineFunnelProps {
  candidates: Candidate[];
}

export const PipelineFunnel: React.FC<PipelineFunnelProps> = ({ candidates }) => {
  // Cumulative funnel calculation: a candidate who reaches a later stage is counted in all preceding stages
  const evaluatedCount = candidates.filter((c) =>
    ["evaluated", "test_sent", "test_done", "interview_scheduled"].includes(c.stage) || c.total_score !== undefined
  ).length;

  const testSentCount = candidates.filter((c) =>
    ["test_sent", "test_done", "interview_scheduled"].includes(c.stage)
  ).length;

  const testDoneCount = candidates.filter((c) =>
    ["test_done", "interview_scheduled"].includes(c.stage) || c.test_code !== undefined
  ).length;

  const scheduledCount = candidates.filter((c) =>
    c.stage === "interview_scheduled"
  ).length;

  const data = [
    { stageName: "Evaluated", stageKey: "evaluated", count: evaluatedCount, color: "#6366f1" },
    { stageName: "Test Sent", stageKey: "test_sent", count: testSentCount, color: "#f59e0b" },
    { stageName: "Test Done", stageKey: "test_done", count: testDoneCount, color: "#3b82f6" },
    { stageName: "Scheduled", stageKey: "interview_scheduled", count: scheduledCount, color: "#10b981" },
  ];

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Screening Funnel</h3>
          <p className="text-xs text-slate-500">Candidate progression by stage</p>
        </div>
        <div className="text-xs font-semibold text-slate-400">
          {candidates.length} total candidates
        </div>
      </div>

      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="stageName" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#64748b" }} />
            <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#64748b" }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#1e293b", borderRadius: "8px", color: "#fff", border: "none", fontSize: "12px" }}
              cursor={{ fill: "rgba(241, 245, 249, 0.6)" }}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
