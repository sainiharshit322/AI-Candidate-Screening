from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import candidates, evaluation, email_router, calendar_router

app = FastAPI(title="Candidate Screening API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Candidate Screening API is running", "docs": "/docs"}

app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
app.include_router(evaluation.router, prefix="/api/evaluate", tags=["evaluation"])
app.include_router(email_router.router, prefix="/api/email", tags=["email"])
app.include_router(calendar_router.router, prefix="/api/calendar", tags=["calendar"])
