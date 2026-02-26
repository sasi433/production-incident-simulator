from fastapi import FastAPI

app = FastAPI(title="Production Incident Simulator")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}