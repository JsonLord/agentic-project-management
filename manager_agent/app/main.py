from fastapi import FastAPI
from app.core.config import settings
from app.api import webhooks

app = FastAPI(title="Manager Agent", version="0.1.0")

app.include_router(webhooks.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0", "env": settings.JULES_PROFILE}
