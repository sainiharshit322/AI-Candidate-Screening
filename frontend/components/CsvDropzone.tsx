"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from "lucide-react";

interface CsvDropzoneProps {
  onFileSelect: (file: File) => void;
  isLoading?: boolean;
  acceptedFileName?: string;
  title?: string;
  subtitle?: string;
}

export const CsvDropzone: React.FC<CsvDropzoneProps> = ({
  onFileSelect,
  isLoading = false,
  acceptedFileName,
  title = "Upload Candidate CSV File",
  subtitle = "Drag & drop your CSV file here, or click to browse",
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith(".csv")) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (file.name.endsWith(".csv")) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
        isDragOver
          ? "border-indigo-500 bg-indigo-50/50 scale-[1.01]"
          : "border-slate-300 hover:border-slate-400 bg-white"
      }`}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".csv"
        className="hidden"
      />
      <div className="flex flex-col items-center justify-center space-y-3">
        <div className="p-4 bg-indigo-50 rounded-full text-indigo-600">
          <UploadCloud className="w-8 h-8" />
        </div>
        <div>
          <h4 className="text-base font-semibold text-slate-800">{title}</h4>
          <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
        </div>

        {selectedFile && (
          <div className="flex items-center space-x-2 bg-slate-100 text-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium mt-2">
            <FileText className="w-4 h-4 text-indigo-600" />
            <span>{selectedFile.name}</span>
            <span className="text-slate-400">
              ({(selectedFile.size / 1024).toFixed(1)} KB)
            </span>
          </div>
        )}

        {isLoading && (
          <div className="flex items-center space-x-2 text-indigo-600 text-xs font-semibold animate-pulse mt-2">
            <div className="w-3 h-3 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Uploading & parsing file...</span>
          </div>
        )}
      </div>
    </div>
  );
};
