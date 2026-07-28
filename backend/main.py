from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import candidates, evaluation, email_router, calendar_router
import os

app = FastAPI(title="Candidate Screening API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render health check ping handles HEAD & GET requests on /
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Candidate Screening API is running", "docs": "/docs"}

app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(evaluation.router, prefix="/api/evaluate", tags=["evaluation"])
app.include_router(email_router.router, prefix="/api/email", tags=["email"])
app.include_router(calendar_router.router, prefix="/api/calendar", tags=["calendar"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
