from fastapi import FastAPI

from app.api.routes.auth import router as auth_router

app = FastAPI(title="DocuWise API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health():
    return {"status": "ok"}
