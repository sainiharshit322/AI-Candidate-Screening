import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { Toaster } from "sonner";
import { Users, Upload, FileCheck, LayoutDashboard } from "lucide-react";

export const metadata: Metadata = {
  title: "AI Candidate Screening Platform",
  description: "AI-powered recruitment automation and screening dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col font-sans">
        {/* Navbar */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-black text-lg shadow-sm">
                AI
              </div>
              <span className="font-bold text-slate-900 text-lg tracking-tight">
                CandidateScreening
              </span>
            </div>

            <nav className="flex items-center space-x-1 sm:space-x-4">
              <Link
                href="/"
                className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:text-indigo-600 hover:bg-slate-100 flex items-center space-x-1.5 transition"
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
              <Link
                href="/candidates"
                className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:text-indigo-600 hover:bg-slate-100 flex items-center space-x-1.5 transition"
              >
                <Users className="w-4 h-4" />
                <span>Candidates</span>
              </Link>
              <Link
                href="/upload"
                className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:text-indigo-600 hover:bg-slate-100 flex items-center space-x-1.5 transition"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Candidates</span>
              </Link>
              <Link
                href="/results"
                className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-700 hover:text-indigo-600 hover:bg-slate-100 flex items-center space-x-1.5 transition"
              >
                <FileCheck className="w-4 h-4" />
                <span>Test Results</span>
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Body */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>

        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
