from datetime import datetime as dt, timezone, timedelta, datetime


def get_user_current_datetime(timezone_offset) -> dt:
    user_timezone = timezone(timedelta(hours=timezone_offset))
    return dt.now(user_timezone).replace(tzinfo=None, microsecond=0)


def is_event_in_past(event_time: str, user_timezone_offset) -> bool:
    event_time_naive = dt.strptime(event_time, "%Y-%m-%d %H:%M")
    user_current_time_naive = get_user_current_datetime(user_timezone_offset)
    return event_time_naive <= user_current_time_naive


def to_utc(user_date_time: datetime, user_offset):
    return user_date_time - timedelta(hours=user_offset)


def to_user_time(date_time: datetime, user_offset):
    return date_time + timedelta(hours=user_offset)
