"use client";

import React, { useState } from "react";
import { CsvDropzone } from "../../components/CsvDropzone";
import { uploadTestResultsCsv, UploadResultsResponse } from "../../lib/api";
import { toast } from "sonner";
import { FileCheck, CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";

export default function ResultsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<UploadResultsResponse | null>(null);
  const [previewRows, setPreviewRows] = useState<any[]>([]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      if (text) {
        const lines = text.split("\n").filter((l) => l.trim().length > 0);
        const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());
        const parsed = lines.slice(1, 6).map((line) => {
          const vals = line.split(",").map((v) => v.trim());
          const obj: any = {};
          headers.forEach((h, i) => {
            obj[h] = vals[i] || "";
          });
          return obj;
        });
        setPreviewRows(parsed);
      }
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a test results CSV file first.");
      return;
    }
    setLoading(true);
    try {
      const res = await uploadTestResultsCsv(selectedFile);
      setResponse(res);
      toast.success(`Test results uploaded! Updated ${res.updated} candidates.`);
    } catch (e: any) {
      toast.error(`Failed to upload test results: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center space-x-2">
          <FileCheck className="w-6 h-6 text-indigo-600" />
          <span>Upload Assessment Test Results</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload candidate test score CSV (columns: Email, Test LA, Test Code) to update composite rankings and trigger interview scheduling.
        </p>
      </div>

      {/* Dropzone */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <CsvDropzone
          onFileSelect={handleFileSelect}
          title="Upload Technical Test Results CSV"
          subtitle="Required columns: Email, Test LA, Test Code (or Coding Score)"
        />

        {/* CSV Preview */}
        {previewRows.length > 0 && (
          <div className="mt-4 space-y-2">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              File Preview (First 5 Rows)
            </h3>
            <div className="overflow-x-auto border border-slate-200 rounded-lg">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200">
                  <tr>
                    {Object.keys(previewRows[0]).map((h, i) => (
                      <th key={i} className="py-2 px-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {previewRows.map((row, idx) => (
                    <tr key={idx}>
                      {Object.values(row).map((val: any, i) => (
                        <td key={i} className="py-2 px-3">{val}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold text-xs rounded-lg shadow-sm flex items-center space-x-2 transition"
          >
            <span>{loading ? "Processing..." : "Submit Test Results"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Response Box */}
      {response && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-emerald-600 font-bold text-sm">
            <CheckCircle2 className="w-5 h-5" />
            <span>Upload Completed Successfully</span>
          </div>

          <p className="text-xs text-slate-700">
            Updated candidate assessment scores for <strong>{response.updated}</strong> candidates. Stage updated to <span className="font-semibold text-blue-600">test_done</span>.
          </p>

          {response.unmatched_emails && response.unmatched_emails.length > 0 && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 space-y-1">
              <div className="font-semibold flex items-center space-x-1">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Unmatched Emails ({response.unmatched_emails.length}):</span>
              </div>
              <ul className="list-disc list-inside text-amber-800">
                {response.unmatched_emails.map((em, i) => (
                  <li key={i}>{em}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
