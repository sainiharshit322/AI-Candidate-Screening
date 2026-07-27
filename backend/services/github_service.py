from github import Github
import os
import re
from datetime import datetime, timezone, timedelta

def extract_github_username(url: str) -> str:
    if not url or not isinstance(url, str):
        return ""
    clean = url.strip().rstrip("/")
    if "github.com/" in clean:
        after_domain = clean.split("github.com/")[1]
        parts = [p for p in after_domain.split("/") if p]
        if parts:
            return parts[0]
    # Fallback regex
    match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', clean)
    if match:
        return match.group(1)
    return clean.split("/")[-1]

def analyze_github(github_url: str) -> dict:
    if not github_url or not isinstance(github_url, str):
        return {"score": 0.0, "summary": "No GitHub URL provided"}
        
    username = extract_github_username(github_url)
    if not username or username.lower() in ["none", "null", "undefined"]:
        return {"score": 0.0, "summary": "No valid GitHub profile provided"}
        
    token = os.getenv("GITHUB_TOKEN")
    
    # Try authenticated Github first, fallback to unauthenticated if token fails
    g = None
    if token:
        try:
            g = Github(token)
            user = g.get_user(username)
            # test call
            _ = user.id
        except Exception as e:
            print(f"GitHub token auth failed, falling back to public API: {e}")
            g = Github()
    else:
        g = Github()

    try:
        user = g.get_user(username)
        repos = list(user.get_repos())[:15]

        total_stars = sum(r.stargazers_count for r in repos)
        repo_count = len(repos)
        languages = set(r.language for r in repos if r.language)
        ai_keywords = ["ml", "ai", "deep", "neural", "llm", "nlp", "vision", "model", "gpt", "bert", "transformer", "learning"]
        ai_repos = [r for r in repos if any(k in (r.name + " " + (r.description or "")).lower() for k in ai_keywords)]

        recent_threshold = datetime.now(timezone.utc) - timedelta(days=90)
        recent_activity = False
        for r in repos:
            if r.pushed_at:
                pushed = r.pushed_at if r.pushed_at.tzinfo else r.pushed_at.replace(tzinfo=timezone.utc)
                if pushed > recent_threshold:
                    recent_activity = True
                    break

        star_score = min(total_stars / 5.0, 20.0)
        repo_score = min((repo_count / 5.0) * 20.0, 20.0)
        lang_score = min((len(languages) / 3.0) * 20.0, 20.0)
        activity_score = 20.0 if recent_activity else 0.0
        ai_score = min((len(ai_repos) / 2.0) * 20.0, 20.0)

        total = star_score + repo_score + lang_score + activity_score + ai_score

        lang_str = ", ".join(list(languages)[:5]) if languages else "None"
        summary = (
            f"@{username} | {repo_count} repos | {total_stars} stars | "
            f"Languages: {lang_str} | "
            f"AI/ML repos: {len(ai_repos)} | "
            f"Recent activity: {'Yes' if recent_activity else 'No'}"
        )
        return {"score": round(total, 1), "summary": summary}
    except Exception as e:
        print(f"Error inspecting GitHub user {username}: {e}")
        return {"score": 0.0, "summary": f"GitHub (@{username}) analysis failed: {str(e)}"}
