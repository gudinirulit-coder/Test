from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Test Time API", version="0.1.0")

TIMEZONE_ALIASES = {
    # Русские названия и алиасы → IANA tz ID
    "екатеринбург": "Asia/Yekaterinburg",
    "yekaterinburg": "Asia/Yekaterinburg",
    "ekaterinburg": "Asia/Yekaterinburg",
    "москва": "Europe/Moscow",
    "moscow": "Europe/Moscow",
}


class TimeConvertRequest(BaseModel):
    # Желаемый часовой пояс: IANA id (например 'Europe/London', 'Asia/Yekaterinburg')
    # или один из русских алиасов из TIMEZONE_ALIASES.
    timezone: str
    # Если задать `time`, то оно будет интерпретировано как HH:MM в UTC.
    # Если `time` не задан — берём текущее время сервера (UTC на момент запроса).
    time: str | None = None


@app.get("/")
def root():
    return {
        "message": "Эндпоинты: /time — время UTC, /date — дата UTC, /date/local — дата локальная, /convert-time — конвертация текущего UTC (и/или указанного HH:MM) в выбранный TZ (IANA timezone).",
    }


def _convert_time(time_str: str | None, timezone_str: str) -> dict:
    tz_input = timezone_str.strip()
    tz_key = tz_input.lower()
    tz_id = TIMEZONE_ALIASES.get(tz_key, tz_input)

    try:
        target_tz = ZoneInfo(tz_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Не удалось распознать часовой пояс '{timezone_str}'. "
                "Укажите IANA timezone (например 'Europe/London', 'Asia/Tokyo', 'Asia/Yekaterinburg') "
                "или один из алиасов: "
                f"{', '.join(sorted(TIMEZONE_ALIASES.keys()))}. "
                f"Техническая ошибка: {e}"
            ),
        )

    if time_str:
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Некорректный формат времени. Используйте HH:MM, например '15:00'.",
            )
        today_utc = datetime.now(timezone.utc).date()
        dt_utc = datetime.combine(today_utc, parsed_time, tzinfo=timezone.utc)
    else:
        # Берём текущее серверное время (UTC) на момент запроса.
        dt_utc = datetime.now(timezone.utc)

    dt_target = dt_utc.astimezone(target_tz)
    return {
        "input": {
            "time": time_str,
            "timezone": timezone_str,
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


@app.get("/convert-time")
def convert_time_get(time: str | None = None, timezone: str = ""):
    """
    GET-вариант для удобства в Swagger:
    - `timezone` (обязателен): IANA id или русский алиас (если поддержан)
    - `time` (опционален): HH:MM, трактуется как время в UTC

    Если `time` не передан — конвертируем текущее серверное UTC время.
    """
    if not timezone:
        raise HTTPException(status_code=400, detail="Параметр 'timezone' обязателен.")
    return _convert_time(time, timezone)


@app.post("/convert-time")
def convert_time(payload: TimeConvertRequest):
    """
    Преобразование времени из UTC в указанный часовой пояс.

    Примеры тела запроса:
    {
      "timezone": "Asia/Yekaterinburg"
    }

    Можно также использовать русские алиасы (не все города):
    {
      "timezone": "Екатеринбург"
    }

    (необязательно) если нужно конвертировать конкретное время:
    {
      "time": "15:00",
      "timezone": "Екатеринбург"
    }
    """
    return _convert_time(payload.time, payload.timezone)
