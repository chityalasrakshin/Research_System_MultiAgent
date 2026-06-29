"""
Research Command Center — FastAPI backend
==========================================
Serves the Swiss-style HTML frontend and exposes a single
POST /run_pipeline endpoint that the browser calls via fetch().

Setup
-----
1.  Copy research-command-center.html next to this file.
2.  pip install fastapi uvicorn python-dotenv
3.  Set GROQ_API_KEY and TAVILY_API_KEY in a .env file (or env vars).
4.  uvicorn app:app --reload --port 8000
5.  Open http://localhost:8000
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Research Command Center",
    description="Multi-agent research pipeline: search → scrape → write → critique.",
    version="2.0.0",
)

BASE_DIR = Path(__file__).parent
HTML_FILE = BASE_DIR / "research-command-center.html"


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class PipelineRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Research topic or question to investigate.",
        examples=["AI agents in software engineering"],
    )


class PipelineResponse(BaseModel):
    search_results: str
    scraped_content: str
    report: str
    feedback: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def serve_frontend() -> FileResponse:
    """Serve the Swiss-style HTML frontend."""
    if not HTML_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "research-command-center.html not found next to app.py. "
                "Download it from the project root and place it here."
            ),
        )
    return FileResponse(HTML_FILE, media_type="text/html")


@app.post("/run_pipeline", response_model=PipelineResponse)
async def run_pipeline(req: PipelineRequest) -> JSONResponse:
    """
    Run the four-stage research pipeline for the given topic.

    Stages
    ------
    1. Search Agent   — Finds recent, reliable sources and URLs.
    2. Reader Agent   — Scrapes the strongest source for deeper context.
    3. Writer         — Synthesises findings into a structured report.
    4. Critic         — Reviews the report and returns quality feedback.

    Returns
    -------
    JSON with keys: search_results, scraped_content, report, feedback.
    All values are plain Markdown strings.
    """
    _require_env("GROQ_API_KEY")
    _require_env("TAVILY_API_KEY")

    try:
        from pipeline import run_research_pipeline  # your existing module

        result: dict = run_research_pipeline(req.topic)
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "pipeline.py not found. "
                "Make sure pipeline.py is in the same directory as app.py. "
                f"Original error: {exc}"
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return JSONResponse(
        content={
            "search_results":  _coerce_str(result.get("search_results")),
            "scraped_content": _coerce_str(result.get("scraped_content")),
            "report":          _coerce_str(result.get("report")),
            "feedback":        _coerce_str(result.get("feedback")),
        }
    )


@app.get("/health", include_in_schema=False)
async def health() -> dict:
    """Lightweight health check used by load-balancers and CI."""
    return {
        "status": "ok",
        "groq_key_set":   bool(os.getenv("GROQ_API_KEY")),
        "tavily_key_set": bool(os.getenv("TAVILY_API_KEY")),
        "html_present":   HTML_FILE.exists(),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_env(key: str) -> None:
    """Raise a 503 with a clear message if a required env-var is missing."""
    if not os.getenv(key):
        raise HTTPException(
            status_code=503,
            detail=(
                f"{key} is not set. "
                "Add it to your .env file or export it in your shell, "
                "then restart the server."
            ),
        )


def _coerce_str(value: object) -> str:
    """Normalise pipeline output to a non-empty string."""
    if value is None:
        return "No output returned."
    if isinstance(value, str):
        return value.strip() or "No output returned."
    return str(value)


# ---------------------------------------------------------------------------
# Dev entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BASE_DIR)],
    )