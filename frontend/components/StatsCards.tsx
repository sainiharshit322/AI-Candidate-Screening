"use client";

import React from "react";
import { Users, FileCheck, Send, CheckCircle2, Award } from "lucide-react";
import { Candidate } from "../lib/api";

interface StatsCardsProps {
  candidates: Candidate[];
}

export const StatsCards: React.FC<StatsCardsProps> = ({ candidates }) => {
  const total = candidates.length;
  const evaluated = total;

  // Test Sent: Only AFTER 'Send Test Links' is clicked (stage is test_sent, test_done, or interview_scheduled)
  const testSent = candidates.filter((c) =>
    ["test_sent", "test_done", "interview_scheduled"].includes(c.stage)
  ).length;

  // Test Done: Only AFTER test results CSV is uploaded (stage is test_done or interview_scheduled)
  const testDone = candidates.filter((c) =>
    ["test_done", "interview_scheduled"].includes(c.stage)
  ).length;

  // Shortlisted: Only AFTER test results CSV is uploaded (stage is test_done or interview_scheduled) AND total_score >= 70%
  const shortlisted = candidates.filter(
    (c) => ["test_done", "interview_scheduled"].includes(c.stage) && (c.total_score || 0) >= 70
  ).length;

  const cards = [
    { title: "Total Applicants", value: total, icon: Users, color: "text-slate-600 bg-slate-100" },
    { title: "Evaluated", value: evaluated, icon: FileCheck, color: "text-indigo-600 bg-indigo-50" },
    { title: "Test Sent", value: testSent, icon: Send, color: "text-amber-600 bg-amber-50" },
    { title: "Test Done", value: testDone, icon: CheckCircle2, color: "text-blue-600 bg-blue-50" },
    { title: "Shortlisted (≥70%)", value: shortlisted, icon: Award, color: "text-emerald-600 bg-emerald-50 font-bold" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">{card.title}</span>
              <div className={`p-2 rounded-lg ${card.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-slate-900">{card.value}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
