from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Test Time API", version="0.1.0")


@app.get("/")
def root():
    return {
        "message": "Эндпоинты: /time — время, /date — дата UTC, /date/local — дата в локальной TZ сервера",
    }


@app.get("/date")
def server_date_utc():
    today = datetime.now(timezone.utc).date()
    return {
        "iso": today.isoformat(),
        "year": today.year,
        "month": today.month,
        "day": today.day,
        "calendar": "UTC",
    }


@app.get("/date/local")
def server_date_local():
    local = datetime.now().astimezone()
    today = local.date()
    return {
        "iso": today.isoformat(),
        "year": today.year,
        "month": today.month,
        "day": today.day,
        "calendar": "local",
        "utc_offset": local.strftime("%z").strip() or None,
        "tz_name": local.tzname(),
    }


@app.get("/time")
def server_time():
    now = datetime.now(timezone.utc)
    return {
        "utc": now.isoformat(),
        "unix": now.timestamp(),
    }
