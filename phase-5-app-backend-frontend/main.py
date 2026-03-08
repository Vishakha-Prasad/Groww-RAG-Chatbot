from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure Phase 3 and Phase 4 modules are importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE3_DIR = PROJECT_ROOT / "phase-3-query-orchestration"
PHASE4_DIR = PROJECT_ROOT / "phase-4-safety-eval"

sys.path.append(str(PHASE3_DIR))
sys.path.append(str(PHASE4_DIR))

from chat_pipeline import answer_query  # type: ignore  # noqa: E402
from guardrails import check_answer  # type: ignore  # noqa: E402


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    intent: str
    safety: Dict[str, Any]
    used_chunks: List[Dict[str, Any]]


app = FastAPI(title="Groww HDFC MF RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root() -> Any:
    """Serve the main chat UI."""
    index_path = static_dir / "index.html"
    return index_path.read_text(encoding="utf-8")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Chat endpoint wiring Phase 3 (orchestration) and Phase 4 (guardrails).
    """
    try:
        phase3_result = answer_query(req.message)
        answer_text: str = phase3_result.get("answer", "")
        intent: str = phase3_result.get("intent", "UNKNOWN")
        used_chunks: List[Dict[str, Any]] = phase3_result.get("used_chunks", [])

        safety = check_answer(answer_text)

        # If advice/personal-info language leaked through, override answer.
        if safety.get("has_advice_language") or safety.get("has_personal_info_language"):
            answer_text = (
                "I can only share factual information about the supported HDFC mutual fund schemes on Groww. "
                "I cannot provide investment advice, recommendations, comparisons, or handle personal information. "
                "Please refer to the official Groww pages such as https://groww.in/mutual-funds/user/explore "
                "for more details."
            )
            safety = check_answer(answer_text)

        # Ensure at least one allowed source URL is present.
        if not safety.get("has_allowed_source_url"):
            answer_text = (
                f"{answer_text.rstrip()} "
                "Source: https://groww.in/mutual-funds/user/explore"
            )
            safety = check_answer(answer_text)

        return ChatResponse(
            answer=answer_text,
            intent=intent,
            safety=safety,
            used_chunks=used_chunks,
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return ChatResponse(
            answer=f"DEBUG ERROR: {str(e)}\n\n{error_detail}",
            intent="ERROR",
            safety={"is_safe": False},
            used_chunks=[],
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

