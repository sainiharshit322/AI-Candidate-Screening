import google.generativeai as genai
import json
import os
import re

async def evaluate_candidate(candidate: dict, job_description: str, resume_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not configured in environment.")
        return {
            "score": 50.0,
            "reasoning": "Gemini API key not configured. Candidate fit scored based on default fallback.",
            "strengths": ["Submitted profile details"],
            "gaps": ["AI key required for model scoring"]
        }

    # Model priority: fast Flash models with high rate limits
    models_to_try = [
        "gemini-3.1-flash-lite"
    ]

    prompt = f"""You are a senior technical recruiter. Score this candidate 0–100 based on fit with the job description.
Return ONLY valid JSON, no markdown formatting, no text before or after the JSON:
{{
  "score": <integer 0-100>,
  "reasoning": "<2-3 sentences explaining match>",
  "strengths": ["<strength1>", "<strength2>"],
  "gaps": ["<gap1>", "<gap2>"]
}}

Job Description:
{job_description}

Candidate Profile:
Name: {candidate.get('name')}
College: {candidate.get('college')}
Branch: {candidate.get('branch')}
CGPA: {candidate.get('cgpa')}
Best AI Project: {str(candidate.get('best_ai_project') or 'Not specified')[:1500]}
Research Work: {str(candidate.get('research_work') or 'Not specified')[:1500]}
Resume Content: {str(resume_text)[:3000] if resume_text else 'Not available'}
"""

    genai.configure(api_key=api_key)
    last_error = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if not response or not response.text:
                continue
                
            text = response.text.strip()
            # Clean markdown codeblocks
            if "```" in text:
                match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
                if match:
                    text = match.group(1)
                else:
                    text = text.replace("```json", "").replace("```", "").strip()

            data = json.loads(text)
            score_val = float(data.get("score", 50.0))
            return {
                "score": score_val,
                "reasoning": str(data.get("reasoning", "Candidate profile evaluated against job requirements.")),
                "strengths": [str(s) for s in data.get("strengths", []) if s],
                "gaps": [str(g) for g in data.get("gaps", []) if g]
            }
        except Exception as e:
            last_error = e
            print(f"Gemini model '{model_name}' evaluation failed: {e}")
            continue

    print(f"All Gemini models failed. Last error: {last_error}")
    return {
        "score": 50.0,
        "reasoning": f"AI Evaluation API Error: {str(last_error)}",
        "strengths": ["Candidate profile data uploaded"],
        "gaps": ["AI model evaluation error"]
    }
