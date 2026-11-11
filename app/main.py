from fastapi import FastAPI

app = FastAPI(title="Web-Project")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
