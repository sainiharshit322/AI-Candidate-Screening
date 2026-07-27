"use client";

import React from "react";
import { Users, FileCheck, Send, CheckCircle2, Calendar } from "lucide-react";
import { Candidate } from "../lib/api";

interface StatsCardsProps {
  candidates: Candidate[];
}

export const StatsCards: React.FC<StatsCardsProps> = ({ candidates }) => {
  const total = candidates.length;

  const evaluated = candidates.filter((c) =>
    ["evaluated", "test_sent", "test_done", "interview_scheduled"].includes(c.stage) || c.total_score !== undefined
  ).length;

  const testSent = candidates.filter((c) =>
    ["test_sent", "test_done", "interview_scheduled"].includes(c.stage)
  ).length;

  const testDone = candidates.filter((c) =>
    ["test_done", "interview_scheduled"].includes(c.stage) || c.test_code !== undefined
  ).length;

  const scheduled = candidates.filter((c) =>
    c.stage === "interview_scheduled"
  ).length;

  const cards = [
    { title: "Total Applicants", value: total, icon: Users, color: "text-slate-600 bg-slate-100" },
    { title: "Evaluated", value: evaluated, icon: FileCheck, color: "text-indigo-600 bg-indigo-50" },
    { title: "Test Sent", value: testSent, icon: Send, color: "text-amber-600 bg-amber-50" },
    { title: "Test Done", value: testDone, icon: CheckCircle2, color: "text-blue-600 bg-blue-50" },
    { title: "Scheduled", value: scheduled, icon: Calendar, color: "text-emerald-600 bg-emerald-50" },
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
