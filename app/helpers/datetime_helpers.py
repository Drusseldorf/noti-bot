from datetime import datetime as dt, timezone, timedelta


def get_user_current_datetime(timezone_offset: int) -> dt:
    user_timezone = timezone(timedelta(hours=timezone_offset))
    return dt.now(user_timezone).replace(tzinfo=None, microsecond=0)


def is_event_in_past(event_time: str, user_timezone_offset: int) -> bool:
    event_time_naive = dt.strptime(event_time, "%d.%m.%Y %H:%M")
    user_current_time_naive = get_user_current_datetime(user_timezone_offset)
    return event_time_naive <= user_current_time_naive
