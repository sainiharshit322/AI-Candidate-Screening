# 🚀 AI-Powered Candidate Screening & Automated Recruitment System

An end-to-end, multi-stage AI recruitment and candidate evaluation platform. The system automates candidate profile ingestion, resume parsing, GitHub repository analysis, Google Gemini Flash AI evaluation, technical assessment link dispatching, composite candidate ranking, and automated Google Calendar / Meet interview scheduling.

---

## 📸 Key Features

- **📄 Automated Resume & Profile Ingestion**: Ingests candidate CSV datasets, parses PDF/DOCX resumes, auto-converts Google Drive view links (`drive.google.com/file/d/...`) into direct download links, and handles duplicate email datasets cleanly with smart sub-aliasing.
- **🤖 Gemini Flash Model Integration**: Uses high-speed, high-rate-limit Google Gemini models (`gemini-1.5-flash`, `gemini-2.0-flash`) to generate candidate match scores (0–100), concise reasoning, candidate strengths, and gaps.
- **🐙 PyGitHub Code & Profile Analyzer**: Parses GitHub user profiles and repository links, calculating metrics based on public repositories, commit activity, star counts, primary languages, and AI/ML project keywords.
- **📧 Resend Email Integration**: Dispatches technical assessment emails and Google Meet interview invitations via the Resend API with dedicated delivery overrides to `sainiharshit322@gmail.com`.
- **📅 Google Calendar & Meet Automation**: Authorizes via Google OAuth2, calculates non-overlapping 30-minute interview slots starting the next business day at 10:00 AM UTC (with 15-minute gaps), creates Google Calendar events, and generates Google Meet video links.
- **📊 Next.js 15 Recruiter Dashboard**: Modern, responsive dashboard built with Next.js 15, TailwindCSS, Lucide Icons, and Recharts, featuring cumulative funnel analytics, interactive candidate drawers, score badges, and candidate deletion controls.

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **AI Model**: Google Generative AI (`google-generativeai` SDK — `gemini-1.5-flash` / `gemini-2.0-flash`)
- **GitHub Analytics**: PyGitHub (`github`)
- **Email Service**: Resend Python SDK (`resend`)
- **Calendar & OAuth**: Google API Client (`google-api-python-client`, `google-auth-oauthlib`)
- **Resume Parsing**: `PyPDF2`, `python-docx`
- **Database**: Supabase PostgreSQL client (`supabase-py`) with safe in-memory fallback (`mock_db`)

### Frontend
- **Framework**: Next.js 15 (App Router), React 19
- **Styling**: TailwindCSS, Lucide React Icons
- **Charts & Data**: Recharts, Axios
- **Notifications**: Sonner Toasts

---

## 🔄 Multi-Stage Recruitment Pipeline Workflow

The platform operates across **4 distinct, sequential stages**:

```
 ┌────────────────────────────────┐
 │ Stage 1: Candidate Upload      │  Ingest CSV dataset & execute AI + GitHub evaluation
 │          & AI/GitHub Screening │  (Initial score based ONLY on Resume + GitHub)
 └──────────────┬─────────────────┘
                │
                ▼
 ┌────────────────────────────────┐
 │ Stage 2: 100% Test Link        │  Click "Send Test Links" to dispatch assessment links
 │          Email Dispatch        │  to 100% of evaluated candidates via Resend
 └──────────────┬─────────────────┘
                │
                ▼
 ┌────────────────────────────────┐
 │ Stage 3: Test Results Upload   │  Upload test results CSV (LA + Code scores)
 │          & Composite Scoring   │  Recalculate final composite score for all candidates
 └──────────────┬─────────────────┘
                │
                ▼
 ┌────────────────────────────────┐
 │ Stage 4: Interview Scheduling  │  Click "Schedule Interviews" to create Google Calendar
 │          (Shortlisted ≥ 70%)   │  slots & Meet links for shortlisted candidates (≥70%)
 └────────────────────────────────┘
```

### 1. Stage 1: Profile Ingestion & AI Screening
- Candidate CSV files are uploaded containing `name`, `email`, `college`, `branch`, `cgpa`, `best_ai_project`, `research_work`, `github_url`, and `resume_url`.
- Gemini Flash evaluates the candidate against the Job Description.
- GitHub service analyzes the candidate's GitHub profile/repo metrics.
- **Initial Score Formula** (prior to test results upload):
  $$\text{Initial Score} = \frac{\text{AI Score} \times 0.35 + \text{GitHub Score} \times 0.25 + \text{CGPA Score} \times 0.05}{0.65}$$
- Candidates transition to `evaluated` stage.

### 2. Stage 2: 100% Test Link Email Dispatch
- Clicking **Send Test Links** sends technical assessment links to **100% of evaluated applicants** without any initial score cutoff.
- Emails are delivered via Resend API (target email hardcoded to `sainiharshit322@gmail.com`).
- Candidates transition to `test_sent` stage.

### 3. Stage 3: Test Results Upload & Final Composite Scoring
- Uploading test results CSV (`s_no, name, email, test_la, test_code`) updates student scores using 4-level flexible candidate matching (`s_no`, `name`, `email`, row position).
- **Final Total Composite Score Formula**:
  $$\text{Final Total Score} = \text{AI Score} \times 0.35 + \text{GitHub Score} \times 0.25 + \text{Test Code} \times 0.25 + \text{Test LA} \times 0.10 + \text{CGPA Score} \times 0.05$$
- Candidates transition to `test_done` stage.

### 4. Stage 4: Shortlisting & Interview Scheduling ($\ge 70\%$)
- A candidate qualifies as **Shortlisted** strictly when they have **completed the assessment test AND achieved a final overall score $\ge 70\%$**.
- Clicking **Schedule Interviews** calculates 30-minute interview slots starting the next business day at 10:00 AM UTC (with 15-minute gaps), creates Google Calendar events, generates Google Meet links, updates stage to `interview_scheduled`, and dispatches invite emails to `sainiharshit322@gmail.com`.

---

## 📂 Project Directory Structure

```
AI-Candidate-Screening/
├── backend/
│   ├── db/
│   │   └── supabase_client.py   # Supabase client & in-memory mock_db
│   ├── models/
│   │   └── schemas.py           # Pydantic v2 data schemas
│   ├── routers/
│   │   ├── candidates.py        # Candidate CSV upload, list, delete & test results
│   │   ├── evaluation.py        # Job description & Gemini + GitHub evaluation
│   │   ├── email_router.py      # Resend test link email dispatching
│   │   └── calendar_router.py   # Google OAuth & Calendar interview scheduling
│   ├── services/
│   │   ├── ai_evaluator.py      # Gemini Flash model fit scoring
│   │   ├── github_service.py    # PyGitHub username extraction & repo analytics
│   │   ├── resume_parser.py     # PDF/DOCX resume & Google Drive link parser
│   │   ├── email_service.py     # Resend email dispatch service
│   │   └── calendar_service.py  # Google Calendar API & Meet link generator
│   ├── main.py                  # FastAPI main application entrypoint & CORS config
│   ├── requirements.txt         # Backend Python dependencies
│   └── .env.example             # Template environment variables
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Dashboard root layout & navigation header
│   │   ├── page.tsx             # Main Recruiter Dashboard page
│   │   ├── candidates/page.tsx  # Candidate Management page
│   │   ├── upload/page.tsx      # Candidate CSV upload page
│   │   └── results/page.tsx     # Test Results CSV upload page
│   ├── components/
│   │   ├── StatsCards.tsx       # Stage metric stats cards
│   │   ├── PipelineFunnel.tsx   # Recharts screening funnel chart
│   │   ├── CandidateTable.tsx   # Searchable & sortable candidate table
│   │   ├── CandidateDrawer.tsx  # Slide-over candidate detail drawer
│   │   └── CsvDropzone.tsx      # Drag & drop CSV file uploader
│   ├── lib/
│   │   └── api.ts               # Typed Axios API client
│   └── package.json             # Frontend dependencies
├── supabase/
│   └── schema.sql               # PostgreSQL tables & foreign key definitions
├── candidate_dataset (1).xlsx - Response.csv    # Sample candidate profiles dataset
├── candidate_dataset (1).xlsx - Test Result.csv  # Sample test results dataset
└── README.md                    # Project documentation
```

---

## ⚙️ Detailed Installation & Setup Instructions

### Prerequisites
- **Python**: Version 3.10 or higher
- **Node.js**: Version 18.0 or higher
- **Git**: Installed on your system
- **API Keys Required**:
  1. **Google AI Studio Key** (`GEMINI_API_KEY`)
  2. **GitHub Personal Access Token** (`GITHUB_TOKEN`)
  3. **Resend API Key** (`RESEND_API_KEY`)
  4. **Google Cloud OAuth 2.0 Credentials** (`GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`)

---

### 1. Backend Setup

#### Step A: Create and Activate Python Virtual Environment
Open a terminal in the project root:

```powershell
cd d:\Harshit\GTM
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Linux / macOS:
source venv/bin/activate
```

#### Step B: Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

#### Step C: Configure Backend Environment Variables
Create a `.env` file in the `backend/` directory:

```ini
# Gemini AI Studio Key
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Credentials (Optional: Leave empty to use resilient in-memory mock_db)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# GitHub Token
GITHUB_TOKEN=github_pat_your_token_here

# Resend Email Config
RESEND_API_KEY=re_your_resend_api_key_here
RESEND_FROM_EMAIL=onboarding@resend.dev

# Google Calendar OAuth Config
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/callback

# Recruiter & Threshold Settings
RECRUITER_EMAIL=sainiharshit322@gmail.com
TEST_LINK=https://hackerrank.com/test-demo
SHORTLIST_THRESHOLD=70
INTERVIEW_THRESHOLD=70
```

#### Step D: Initialize Supabase Database (Optional)
If using Supabase, copy the contents of `supabase/schema.sql` and run them in your **Supabase SQL Editor** to create the `candidates`, `job_descriptions`, `evaluations`, and `interviews` tables.

#### Step E: Start the FastAPI Backend Server
```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```
*The backend API will run at `http://localhost:8000` with interactive API docs at `http://localhost:8000/docs`.*

---

### 2. Frontend Setup

#### Step A: Install Node Dependencies
Open a new terminal window:

```cmd
cd d:\Harshit\GTM\frontend
npm install
```

#### Step B: Configure Frontend Environment
Create a `.env.local` file in `frontend/`:

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Step C: Start Next.js Development Server
```cmd
cd frontend
npm run dev
```
*The Recruiter Dashboard will run at `http://localhost:3000`.*

---

### 3. Google OAuth 2.0 Authorization Setup for Calendar Scheduling

1. Go to the **Google Cloud Console** -> **APIs & Services** -> **Credentials**.
2. Create an **OAuth 2.0 Client ID** (Application Type: **Web application**).
3. Set Authorized Redirect URIs to:
   `http://localhost:8000/api/calendar/callback`
4. Copy the Client ID and Client Secret into your `backend/.env` file.
5. In your browser, open `http://localhost:8000/api/calendar/auth` to authenticate your Google Account and grant Calendar access.

---

## 📡 API Reference Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/candidates/upload` | Upload candidate CSV dataset |
| `GET` | `/api/candidates` | List all candidates with latest scores and stage |
| `GET` | `/api/candidates/{id}` | Retrieve candidate details |
| `DELETE` | `/api/candidates/{id}` | Delete a candidate record |
| `DELETE` | `/api/candidates/clear-all` | Clear all candidates from the database |
| `PATCH` | `/api/candidates/{id}/stage` | Update candidate stage manually |
| `POST` | `/api/candidates/upload-results` | Upload test results CSV and calculate composite score |
| `POST` | `/api/evaluate/job-description` | Save target Job Description |
| `POST` | `/api/evaluate` | Trigger AI + GitHub evaluation for candidates |
| `GET` | `/api/evaluate/results` | Get ranked shortlisted candidates |
| `POST` | `/api/email/send-test-links` | Dispatch test assessment links to 100% of candidates |
| `POST` | `/api/calendar/schedule` | Schedule 30-min interview slots for shortlisted candidates ($\ge 70\%$) |
| `GET` | `/api/calendar/auth` | Initiate Google OAuth2 login flow |
| `GET` | `/api/calendar/callback` | Google OAuth2 callback handler |

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
