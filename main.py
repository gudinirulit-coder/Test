from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Test Time API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "GET /time для текущего времени сервера"}


@app.get("/time")
def server_time():
    now = datetime.now(timezone.utc)
    return {
        "utc": now.isoformat(),
        "unix": now.timestamp(),
    }
