from datetime import datetime, time as time_cls, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Test Time API", version="0.1.0")


SUPPORTED_TIMEZONES = {
    # Russian names and aliases → IANA tz IDs
    "екатеринбург": "Asia/Yekaterinburg",
    "yekaterinburg": "Asia/Yekaterinburg",
    "ekaterinburg": "Asia/Yekaterinburg",
    "москва": "Europe/Moscow",
    "moscow": "Europe/Moscow",
}


class TimeConvertRequest(BaseModel):
    time: str
    timezone: str


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


@app.post("/convert-time")
def convert_time(payload: TimeConvertRequest):
    """
    Преобразование времени из UTC в указанный часовой пояс.

    Примеры тела запроса:
    {
      "time": "15:00",
      "timezone": "Екатеринбург"
    }
    """
    try:
        parsed_time = datetime.strptime(payload.time, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Некорректный формат времени. Используйте HH:MM, например '15:00'.",
        )

    tz_key = payload.timezone.strip().lower()
    if tz_key not in SUPPORTED_TIMEZONES:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестный часовой пояс '{payload.timezone}'. "
            f"Поддерживаемые варианты: {', '.join(sorted(SUPPORTED_TIMEZONES.keys()))}",
        )

    today_utc = datetime.now(timezone.utc).date()
    dt_utc = datetime.combine(today_utc, parsed_time, tzinfo=timezone.utc)

    target_tz = ZoneInfo(SUPPORTED_TIMEZONES[tz_key])
    dt_target = dt_utc.astimezone(target_tz)

    return {
        "input": {
            "time": payload.time,
            "timezone": payload.timezone,
            "assumed_zone": "UTC",
        },
        "utc": dt_utc.isoformat(),
        "converted": {
            "time": dt_target.strftime("%H:%M"),
            "iso": dt_target.isoformat(),
            "timezone": target_tz.key,
            "utc_offset": dt_target.strftime("%z"),
        },
    }
