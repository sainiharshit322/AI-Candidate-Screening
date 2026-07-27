import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface Candidate {
  id: string;
  s_no?: number;
  name?: string;
  email: string;
  college?: string;
  branch?: string;
  cgpa?: number;
  best_ai_project?: string;
  research_work?: string;
  github_url?: string;
  resume_url?: string;
  stage: string;
  created_at?: string;
  evaluation_id?: string;
  total_score?: number;
  ai_score?: number;
  ai_reasoning?: string;
  ai_strengths?: string[];
  ai_gaps?: string[];
  github_score?: number;
  github_summary?: string;
  test_la?: number;
  test_code?: number;
}

export interface JobDescription {
  id: string;
  title?: string;
  content: string;
  created_at?: string;
}

export interface UploadResponse {
  inserted: number;
  updated: number;
}

export interface UploadResultsResponse {
  updated: number;
  unmatched_emails: string[];
}

export interface ScheduleResult {
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  scheduled_at: string;
  google_meet_link: string;
  calendar_event_id: string;
}

export const uploadCandidatesCsv = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post<UploadResponse>("/api/candidates/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const listCandidates = async (): Promise<Candidate[]> => {
  const res = await api.get<Candidate[]>("/api/candidates");
  return res.data;
};

export const getCandidate = async (id: string): Promise<Candidate> => {
  const res = await api.get<Candidate>(`/api/candidates/${id}`);
  return res.data;
};

export const deleteCandidate = async (id: string): Promise<{ success: boolean; deleted_id: string }> => {
  const res = await api.delete<{ success: boolean; deleted_id: string }>(`/api/candidates/${id}`);
  return res.data;
};

export const clearAllCandidates = async (): Promise<{ success: boolean; count: number }> => {
  const res = await api.delete<{ success: boolean; count: number }>("/api/candidates/clear-all");
  return res.data;
};

export const updateCandidateStage = async (id: string, stage: string): Promise<{ success: boolean; stage: string }> => {
  const res = await api.patch<{ success: boolean; stage: string }>(`/api/candidates/${id}/stage`, { stage });
  return res.data;
};

export const uploadTestResultsCsv = async (file: File): Promise<UploadResultsResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post<UploadResultsResponse>("/api/candidates/upload-results", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const saveJobDescription = async (content: string, title: string = "Job Description"): Promise<JobDescription> => {
  const res = await api.post<JobDescription>("/api/evaluate/job-description", { title, content });
  return res.data;
};

export const triggerEvaluation = async (jobDescriptionId: string): Promise<{ evaluated: number }> => {
  const res = await api.post<{ evaluated: number }>("/api/evaluate", { job_description_id: jobDescriptionId });
  return res.data;
};

export const getShortlistedResults = async (threshold?: number): Promise<Candidate[]> => {
  const url = threshold ? `/api/evaluate/results?threshold=${threshold}` : "/api/evaluate/results";
  const res = await api.get<Candidate[]>(url);
  return res.data;
};

export const sendTestLinks = async (threshold?: number): Promise<{ sent_count: number; results: any[] }> => {
  const url = threshold ? `/api/email/send-test-links?threshold=${threshold}` : "/api/email/send-test-links";
  const res = await api.post<{ sent_count: number; results: any[] }>(url);
  return res.data;
};

export const scheduleInterviews = async (threshold?: number): Promise<{ scheduled_count: number; interviews: ScheduleResult[] }> => {
  const url = threshold ? `/api/calendar/schedule?threshold=${threshold}` : "/api/calendar/schedule";
  const res = await api.post<{ scheduled_count: number; interviews: ScheduleResult[] }>(url);
  return res.data;
};
