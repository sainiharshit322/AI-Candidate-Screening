# Script: commit_and_push.ps1
# Description: Automates git branching, file-level Conventional Commits, skipping root .md files, and pushing branches.

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Starting Senior Developer Git Commit Flow " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

function Invoke-GitCommand {
    param (
        [string]$Command,
        [string[]]$Arguments
    )
    Write-Host "--> Executing: git $Command ($($Arguments -join ' '))" -ForegroundColor Yellow
    & git $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Git command failed: git $Command ($($Arguments -join ' '))"
    }
}

# ----------------------------------------------------
# Step 1: Ensure master branch is established
# ----------------------------------------------------
Write-Host "`n[Step 1/7] Initializing master branch..." -ForegroundColor Green
$hasMaster = git branch --list master
if ($hasMaster) {
    Invoke-GitCommand "checkout" @("master")
} else {
    Invoke-GitCommand "branch" @("-m", "master")
}

# Add .gitignore as root commit on master if not committed
$status = git status --porcelain
if ($status -like "* .gitignore*" -or $status -like "?? .gitignore*") {
    Invoke-GitCommand "add" @(".gitignore")
    Invoke-GitCommand "commit" @(
        "-m", "chore(git): add gitignore rules for environment secrets and python caches",
        "-m", "Prevent accidental tracking of .env configuration files, Python bytecode compilation caches, and IDE artifacts."
    )
}

# Helper to safely recreate branch from master
function Start-FeatureBranch {
    param ([string]$BranchName)
    $exists = git branch --list $BranchName
    if ($exists) {
        Invoke-GitCommand "branch" @("-D", $BranchName)
    }
    Invoke-GitCommand "checkout" @("-b", $BranchName)
}

# ----------------------------------------------------
# Branch 1: Database Schema
# ----------------------------------------------------
Write-Host "`n[Step 2/7] Processing Branch: feat/database-schema..." -ForegroundColor Green
Start-FeatureBranch "feat/database-schema"

$status = git status --porcelain
if ($status -like "*supabase/schema.sql*" -or $status -like "?? supabase/schema.sql*") {
    Invoke-GitCommand "add" @("supabase/schema.sql")
    Invoke-GitCommand "commit" @(
        "-m", "feat(db): initialize PostgreSQL schema for candidate screening pipeline",
        "-m", "Establish relational tables for candidates, job descriptions, evaluations, and interviews with UUID primary keys, foreign key constraints, and automatic timestamps."
    )
}

Invoke-GitCommand "checkout" @("master")
Invoke-GitCommand "merge" @("feat/database-schema")

# ----------------------------------------------------
# Branch 2: Backend Core Infrastructure
# ----------------------------------------------------
Write-Host "`n[Step 3/7] Processing Branch: feat/backend-core-infra..." -ForegroundColor Green
Start-FeatureBranch "feat/backend-core-infra"

Invoke-GitCommand "add" @("backend/requirements.txt")
Invoke-GitCommand "commit" @(
    "-m", "chore(deps): add backend dependencies for FastAPI, Supabase, OpenAI, and Google APIs",
    "-m", "Specify pinned dependencies for FastAPI runtime, Pydantic data validation, Supabase client, PyPDF2 resume parsing, and Google OAuth services."
)

Invoke-GitCommand "add" @("backend/Dockerfile")
Invoke-GitCommand "commit" @(
    "-m", "ci(docker): add multi-stage container build spec for FastAPI app",
    "-m", "Define Docker image environment for containerized deployment of the candidate screening backend service."
)

Invoke-GitCommand "add" @("backend/.env.example")
Invoke-GitCommand "commit" @(
    "-m", "config(env): provide environment template for DB and LLM API keys",
    "-m", "Document required environment variables including Supabase database URL, key credentials, and OpenAI API settings."
)

Invoke-GitCommand "add" @("backend/db/supabase_client.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(db): establish Supabase connection client and table helpers",
    "-m", "Implement lazy client initialization and database query helper methods for CRUD operations on candidate records."
)

Invoke-GitCommand "add" @("backend/models/schemas.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(models): define Pydantic schemas for candidate ingestion and scoring",
    "-m", "Add request/response models for candidate creation, job description ingestion, evaluation results, and interview scheduling payloads."
)

Invoke-GitCommand "add" @("backend/main.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(server): setup FastAPI runtime bootstrap, CORS middleware, and API routing",
    "-m", "Initialize primary FastAPI application, configure wildcard CORS policies, and mount domain routers under /api prefixes."
)

Invoke-GitCommand "checkout" @("master")
Invoke-GitCommand "merge" @("feat/backend-core-infra")

# ----------------------------------------------------
# Branch 3: Candidate Evaluation Engine
# ----------------------------------------------------
Write-Host "`n[Step 4/7] Processing Branch: feat/candidate-evaluation-engine..." -ForegroundColor Green
Start-FeatureBranch "feat/candidate-evaluation-engine"

Invoke-GitCommand "add" @("backend/services/resume_parser.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(service): add PDF text extraction and resume parsing module",
    "-m", "Implement PyPDF2 text extractor to parse applicant resume documents into raw text strings for LLM evaluation."
)

Invoke-GitCommand "add" @("backend/services/github_service.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(service): integrate GitHub API for repository metrics and code audit",
    "-m", "Extract developer signals including repository count, stars, primary languages, and recent activity from GitHub user profiles."
)

Invoke-GitCommand "add" @("backend/services/ai_evaluator.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(service): build LLM candidate evaluation and multi-criteria scoring service",
    "-m", "Implement OpenAI prompt engineering for resume relevance, GitHub code quality assessment, strengths/gaps identification, and composite score calculation."
)

Invoke-GitCommand "add" @("backend/routers/candidates.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(api): implement candidate management and resume ingestion endpoints",
    "-m", "Add endpoints for candidate registration, profile listing, detail retrieval, and multipart resume file upload."
)

Invoke-GitCommand "add" @("backend/routers/evaluation.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(api): expose candidate evaluation trigger and scorecard endpoints",
    "-m", "Define API routes to trigger async candidate evaluations, fetch AI scorecards, and retrieve detailed diagnostic breakdowns."
)

Invoke-GitCommand "checkout" @("master")
Invoke-GitCommand "merge" @("feat/candidate-evaluation-engine")

# ----------------------------------------------------
# Branch 4: Integrations (Calendar & Email)
# ----------------------------------------------------
Write-Host "`n[Step 5/7] Processing Branch: feat/integrations-calendar-email..." -ForegroundColor Green
Start-FeatureBranch "feat/integrations-calendar-email"

Invoke-GitCommand "add" @("backend/services/calendar_service.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(service): implement Google Calendar OAuth2 client for interview scheduling",
    "-m", "Build service layer to handle Google API credentials, query free/busy availability, and create Google Meet calendar invitations."
)

Invoke-GitCommand "add" @("backend/routers/calendar_router.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(api): expose calendar slot availability and meet booking endpoints",
    "-m", "Provide REST endpoints for fetching available interview time slots and booking interviews directly with candidates."
)

Invoke-GitCommand "add" @("backend/services/email_service.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(service): build email dispatch service with automated candidate templating",
    "-m", "Implement SMTP email service to send candidate invitations, interview confirmations, and screening decision status updates."
)

Invoke-GitCommand "add" @("backend/routers/email_router.py")
Invoke-GitCommand "commit" @(
    "-m", "feat(api): expose notification trigger endpoints for candidate updates",
    "-m", "Define API routes for triggering automated candidate email communications and interview reminder notifications."
)

Invoke-GitCommand "checkout" @("master")
Invoke-GitCommand "merge" @("feat/integrations-calendar-email")

# ----------------------------------------------------
# Branch 5: Test Suite
# ----------------------------------------------------
Write-Host "`n[Step 6/7] Processing Branch: feat/test-suite..." -ForegroundColor Green
Start-FeatureBranch "feat/test-suite"

Invoke-GitCommand "add" @("backend/test_api.py")
Invoke-GitCommand "commit" @(
    "-m", "test(api): add smoke tests for FastAPI server and candidate CRUD",
    "-m", "Verify root endpoint availability, health status responses, and basic candidate creation workflows."
)

Invoke-GitCommand "add" @("backend/test_phase2.py")
Invoke-GitCommand "commit" @(
    "-m", "test(evaluation): add integration test suite for resume parsing and AI scoring",
    "-m", "Implement automated tests validating resume text extraction, GitHub profile auditing, and AI evaluation response schemas."
)

Invoke-GitCommand "add" @("backend/test_phase3.py")
Invoke-GitCommand "commit" @(
    "-m", "test(integrations): add end-to-end integration tests for calendar and email dispatch",
    "-m", "Implement automated test suite verifying Google Calendar event scheduling and email notification delivery pipelines."
)

Invoke-GitCommand "checkout" @("master")
Invoke-GitCommand "merge" @("feat/test-suite")

# ----------------------------------------------------
# Step 7: Commit Script Itself
# ----------------------------------------------------
Write-Host "`n[Step 7/7] Committing PowerShell script to repository..." -ForegroundColor Green
Invoke-GitCommand "add" @("commit_and_push.ps1")
Invoke-GitCommand "commit" @(
    "-m", "chore(ci): add commit_and_push.ps1 script for automated modular git workflow",
    "-m", "Script encapsulates multi-branch creation, Conventional Commit execution, skipping root documentation, and remote pushing."
)

# ----------------------------------------------------
# Remote Push
# ----------------------------------------------------
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host " Checking Remote Repository Configuration " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$remotes = git remote
if ($remotes -contains "origin") {
    Write-Host "Remote 'origin' found. Pushing all branches..." -ForegroundColor Green
    $branches = @("master", "feat/database-schema", "feat/backend-core-infra", "feat/candidate-evaluation-engine", "feat/integrations-calendar-email", "feat/test-suite")
    foreach ($branch in $branches) {
        Write-Host "--> Pushing branch $branch to origin..." -ForegroundColor Yellow
        git push -u origin $branch
    }
    Write-Host "`nAll branches successfully pushed to GitHub remote!" -ForegroundColor Green
} else {
    Write-Host "`n[NOTICE] Remote 'origin' is not yet configured." -ForegroundColor Yellow
    Write-Host "All commits and feature branches have been created locally!" -ForegroundColor Green
    Write-Host "To push these branches to GitHub, run:" -ForegroundColor White
    Write-Host "  git remote add origin <YOUR_GITHUB_REPO_URL>" -ForegroundColor Cyan
    Write-Host "  git push --all origin" -ForegroundColor Cyan
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host " Workflow Completed Successfully! " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
