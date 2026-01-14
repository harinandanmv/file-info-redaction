from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
<<<<<<< HEAD
from app.core.pipeline import PIIPipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Pipeline..")
    try:
        app.state.pii_pipeline = PIIPipeline()
        print("Pipeline Loaded Successfully!")
    except Exception:
        raise
    yield
    print("Shutting down Pipeline!")
=======
from app.db.database import engine
from app.db.models import Base

>>>>>>> d7717be661868476581ddf3cec50899a73a438b1

app = FastAPI(
    title="Insurance PII Redaction API",
    lifespan = lifespan,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")

@app.get("/")
def health():
    return {"status": "ok"}