import logging
import time
import uuid
import asyncio
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from knowledge_agent import ask

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("knowledge-agent")

app = FastAPI(title="Knowledge Agent API", version="0.2.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str = "default"


class ChatResponse(BaseModel):
    request_id: str
    answer: str
    session_id: str
    latency_ms: float


def sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_stream():
        started = time.perf_counter()

        yield sse("status", {"message": "agent started"})

        try:
            # ask() 是同步函数，放到线程里执行，避免阻塞事件循环
            answer = await asyncio.to_thread(
                ask, req.message, req.session_id
            )
        except Exception as exc:
            yield sse("error", {"detail": str(exc)})
            return

        latency_ms = round((time.perf_counter() - started) * 1000, 1)

        yield sse("answer", {"answer": answer})
        yield sse(
            "done",
            {
                "session_id": req.session_id,
                "latency_ms": latency_ms,
            },
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    request_id = uuid.uuid4().hex[:12]
    started = time.perf_counter()

    logger.info(
        "chat start request_id=%s session_id=%s message=%s",
        request_id,
        req.session_id,
        req.message,
    )

    try:
        answer = ask(req.message, thread_id=req.session_id)
    except Exception as exc:
        logger.exception(
            "chat failed request_id=%s session_id=%s error=%s",
            request_id,
            req.session_id,
            exc,
        )
        raise HTTPException(status_code=500, detail=str(exc))

    latency_ms = round((time.perf_counter() - started) * 1000, 1)

    logger.info(
        "chat done request_id=%s session_id=%s latency_ms=%s",
        request_id,
        req.session_id,
        latency_ms,
    )

    return ChatResponse(
        request_id=request_id,
        answer=answer,
        session_id=req.session_id,
        latency_ms=latency_ms,
    )