from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from routers import board_router, task_router
from seed import seed_if_empty

init_db()
seed_if_empty()

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(board_router.router)
app.include_router(task_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
