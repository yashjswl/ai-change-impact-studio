from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .db.base import Base, engine
from .routers import (
    approvals,
    audit,
    comms,
    diff,
    documents,
    exports,
    heatmap,
    impact,
    projects,
    raci,
    raid,
    training,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Change Impact Studio API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(projects.portfolio_router)
app.include_router(documents.router)
app.include_router(impact.router)
app.include_router(heatmap.router)
app.include_router(raci.router)
app.include_router(raci.item_router)
app.include_router(raid.router)
app.include_router(raid.item_router)
app.include_router(comms.router)
app.include_router(comms.item_router)
app.include_router(training.router)
app.include_router(training.item_router)
app.include_router(diff.router)
app.include_router(approvals.router)
app.include_router(audit.router)
app.include_router(exports.router)
app.include_router(exports.download_router)


@app.get("/health")
def health():
    return {"status": "ok"}
