# backend/main.py
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .llm_client import generate_diagnosis
from .db import init_db, save_query, get_history

app = FastAPI(title="Healthcare Symptom Checker API")

# CORS setup: allow configured origins or all (*) by default
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
cors_origins = [o.strip() for o in cors_origins if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if cors_origins == ["*"] else cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()

class Request(BaseModel):
    text: str
    user_id: str | None = None

@app.post("/api/diagnose")
def diagnose(req: Request):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="No symptoms provided")
    
    response = generate_diagnosis(req.text)
    save_query(req.user_id, req.text, response)
    return {"result": response, "disclaimer": "Educational purpose only."}

@app.get("/api/logs")
def get_logs():
    conn = sqlite3.connect("symptom_history.db")
    c = conn.cursor()
    c.execute("SELECT id, symptoms, response, created_at FROM history ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()

    return {"logs": [{"id": r[0], "symptom": r[1], "response": r[2], "created_at": r[3]} for r in rows]}


class Feedback(BaseModel):
    time: str | None = None
    rating: int | None = None
    feedback: str | None = None
    result: str | None = None


@app.post("/api/feedback", status_code=201)
def submit_feedback(_: Feedback):
    # Minimal endpoint so the frontend can submit; extend to persist if needed
    return {"status": "ok"}

