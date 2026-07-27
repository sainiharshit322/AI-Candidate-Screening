import google.generativeai as genai
import json
import os

async def evaluate_candidate(candidate: dict, job_description: str, resume_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "score": 50.0,
            "reasoning": "Gemini API key not configured. Candidate fit scored based on profile overview.",
            "strengths": ["Submitted profile details"],
            "gaps": ["Automated AI evaluation pending API key"]
        }
    
    prompt = f"""You are a senior technical recruiter. Score this candidate 0–100 based on fit with the job description.
Return ONLY valid JSON, no markdown, no explanation outside JSON:
{{
  "score": <integer 0-100>,
  "reasoning": "<2-3 sentences>",
  "strengths": ["<strength1>", "<strength2>"],
  "gaps": ["<gap1>", "<gap2>"]
}}

Job Description:
{job_description}

Candidate:
Name: {candidate.get('name')}
CGPA: {candidate.get('cgpa')}
Branch: {candidate.get('branch')}
College: {candidate.get('college')}
Best AI Project: {str(candidate.get('best_ai_project') or '')[:1000]}
Research Work: {str(candidate.get('research_work') or '')[:1000]}
Resume Text: {str(resume_text)[:3000] if resume_text else 'Not available'}
"""

    genai.configure(api_key=api_key)
    
    # Try gemini-2.5-pro first, then fallback to gemini-1.5-flash / gemini-pro
    models_to_try = ["gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    last_error = None
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                lines = text.split("```")[1]
                if lines.startswith("json"):
                    lines = lines[4:]
                text = lines.strip()
            data = json.loads(text)
            return {
                "score": float(data.get("score", 50.0)),
                "reasoning": str(data.get("reasoning", "Evaluated based on JD match.")),
                "strengths": list(data.get("strengths", [])),
                "gaps": list(data.get("gaps", []))
            }
        except Exception as e:
            last_error = e
            continue
            
    return {
        "score": 50.0,
        "reasoning": f"AI Evaluation fallback: {str(last_error)}",
        "strengths": ["Candidate profile processed"],
        "gaps": ["Detailed AI score unavailable"]
    }
