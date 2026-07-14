from fastapi import FastAPI

from app.api.checks import router as checks_router
from app.models.database import Base, engine

app = FastAPI(title="Bank Docs Check Service")

app.include_router(checks_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
