import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from services.github_service import analyze_github
from services.ai_evaluator import evaluate_candidate

async def main():
    print("--- Testing GitHub Analyzer on Dataset URLs ---")
    urls = [
        "https://github.com/pranchalkumar001",
        "https://github.com/Saurav2K03",
        "https://github.com/saifahmed8521",
        "https://github.com/Abhinandan132/Deceptive-Simplicity-High-F1-scores-due-to-artifact-obscuration-",
        "https://github.com/YUVRAJ-SINGH-GANESHJI"
    ]
    for url in urls:
        res = analyze_github(url)
        print(f"URL: {url}\n  Score: {res['score']}, Summary: {res['summary']}\n")

    print("--- Testing Gemini AI Evaluator ---")
    candidate_sample = {
        "name": "Student 1",
        "college": "Delhi Technological University",
        "branch": "Engineering Physics",
        "cgpa": 7.0,
        "best_ai_project": "Developed a CNN-based Leukemia Detection system during my Machine Learning Research Internship at DTU...",
        "research_work": "InViTNet — Hybrid Transformer-Convolution Vision-Language Model..."
    }
    jd = "Software Engineer specialized in Deep Learning, PyTorch, computer vision, and Transformer architectures."
    ai_res = await evaluate_candidate(candidate_sample, jd, "Sample resume content extracted")
    print(f"AI Score: {ai_res['score']}\nReasoning: {ai_res['reasoning']}\nStrengths: {ai_res['strengths']}\nGaps: {ai_res['gaps']}\n")

if __name__ == "__main__":
    asyncio.run(main())
