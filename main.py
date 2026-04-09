from fastapi import FastAPI

app = FastAPI(title="DocuWise API")


@app.get("/health")
def health():
    return {"status": "ok"}
