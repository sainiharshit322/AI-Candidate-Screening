"use client";

import React, { useState } from "react";
import { CsvDropzone } from "../../components/CsvDropzone";
import { saveJobDescription, uploadCandidatesCsv, triggerEvaluation, JobDescription } from "../../lib/api";
import { toast } from "sonner";
import { FileText, Upload, Play, CheckCircle2 } from "lucide-react";

export default function UploadPage() {
  const [jdTitle, setJdTitle] = useState("Senior AI / Software Engineer");
  const [jdContent, setJdContent] = useState(
    "Looking for a strong software engineer proficient in Python, PyTorch, Fast API, PostgreSQL, and LLM model integrations. 3+ years experience with AI systems preferred."
  );
  const [savedJd, setSavedJd] = useState<JobDescription | null>(null);
  const [savingJd, setSavingJd] = useState(false);

  const [uploadingCsv, setUploadingCsv] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ inserted: number; updated: number } | null>(null);

  const [evaluating, setEvaluating] = useState(false);

  const handleSaveJd = async () => {
    if (!jdContent.trim()) {
      toast.error("Please enter job description text.");
      return;
    }
    setSavingJd(true);
    try {
      const res = await saveJobDescription(jdContent, jdTitle);
      setSavedJd(res);
      toast.success(`Job Description saved successfully! UUID: ${res.id}`);
    } catch (e: any) {
      toast.error(`Failed to save JD: ${e.message}`);
    } finally {
      setSavingJd(false);
    }
  };

  const handleCsvSelect = async (file: File) => {
    setUploadingCsv(true);
    try {
      const res = await uploadCandidatesCsv(file);
      setUploadResult(res);
      toast.success(`CSV Uploaded! Inserted: ${res.inserted}, Updated: ${res.updated}`);
    } catch (e: any) {
      toast.error(`CSV upload failed: ${e.message}`);
    } finally {
      setUploadingCsv(false);
    }
  };

  const handleRunEvaluation = async () => {
    if (!savedJd) {
      toast.error("Please save a Job Description first before running evaluation.");
      return;
    }
    setEvaluating(true);
    try {
      const res = await triggerEvaluation(savedJd.id);
      toast.success(`Evaluation complete! Evaluated ${res.evaluated} candidates.`);
    } catch (e: any) {
      toast.error(`Evaluation failed: ${e.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center space-x-2">
          <Upload className="w-6 h-6 text-indigo-600" />
          <span>Upload Candidates & Set Job Description</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Define job requirements, bulk upload candidate CSV files, and trigger AI screening.
        </p>
      </div>

      {/* Section 1: Job Description Input */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
          <FileText className="w-4 h-4 text-indigo-600" />
          <span>Step 1: Define Job Description</span>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">Job Title</label>
          <input
            type="text"
            value={jdTitle}
            onChange={(e) => setJdTitle(e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">Job Description Content</label>
          <textarea
            rows={5}
            value={jdContent}
            onChange={(e) => setJdContent(e.target.value)}
            placeholder="Paste complete JD text here..."
            className="w-full p-3 text-xs bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
          />
        </div>

        <div className="flex items-center justify-between pt-2">
          <button
            onClick={handleSaveJd}
            disabled={savingJd}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            {savingJd ? "Saving JD..." : "Save Job Description"}
          </button>

          {savedJd && (
            <div className="flex items-center space-x-1.5 text-xs text-emerald-600 font-semibold bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-4 h-4" />
              <span>Saved JD ID: {savedJd.id.substring(0, 8)}...</span>
            </div>
          )}
        </div>
      </div>

      {/* Section 2: CSV Upload */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
          <Upload className="w-4 h-4 text-indigo-600" />
          <span>Step 2: Upload Candidates CSV</span>
        </div>

        <CsvDropzone
          onFileSelect={handleCsvSelect}
          isLoading={uploadingCsv}
          title="Upload Candidates CSV"
          subtitle="Columns: S.No, Name, Email, College, Branch, CGPA, Best AI Project, Research Work, GitHub, Resume"
        />

        {uploadResult && (
          <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg text-xs text-indigo-900 flex items-center justify-between">
            <span className="font-semibold">CSV Processing Result:</span>
            <span>
              Inserted: <strong>{uploadResult.inserted}</strong> | Updated: <strong>{uploadResult.updated}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Section 3: Trigger Evaluation */}
      <div className="bg-slate-900 text-white p-6 rounded-xl shadow-md flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold">Step 3: Trigger AI Candidate Screening</h3>
          <p className="text-xs text-slate-300 mt-1">
            Downloads candidate resumes, analyzes GitHub activity, and prompts Gemini AI for scoring.
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={evaluating || !savedJd}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs rounded-lg shadow-md flex items-center space-x-2 transition"
        >
          <Play className="w-4 h-4" />
          <span>{evaluating ? "Running Evaluation..." : "Run AI Evaluation"}</span>
        </button>
      </div>
    </div>
  );
}
