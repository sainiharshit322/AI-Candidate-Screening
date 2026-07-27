-- Candidates table
CREATE TABLE candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  s_no INT,
  name TEXT,
  email TEXT UNIQUE NOT NULL,
  college TEXT,
  branch TEXT,
  cgpa FLOAT,
  best_ai_project TEXT,
  research_work TEXT,
  github_url TEXT,
  resume_url TEXT,
  stage TEXT DEFAULT 'uploaded',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job Descriptions table
CREATE TABLE job_descriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evaluations table
CREATE TABLE evaluations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
  job_description_id UUID REFERENCES job_descriptions(id),
  resume_text TEXT,
  ai_score FLOAT,
  ai_reasoning TEXT,
  ai_strengths JSONB,
  ai_gaps JSONB,
  github_score FLOAT,
  github_summary TEXT,
  test_la FLOAT,
  test_code FLOAT,
  total_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Interviews table
CREATE TABLE interviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
  scheduled_at TIMESTAMPTZ,
  google_meet_link TEXT,
  calendar_event_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
