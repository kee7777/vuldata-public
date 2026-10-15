from datetime import datetime, timedelta

def parse_user_date(date_str: str) -> datetime:
    """Convert YYYY-MM-DD to a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")

def end_of_day(dt: datetime) -> datetime:
    """Return datetime object at 23:59:59 of the given day."""
    return dt + timedelta(hours=23, minutes=59, seconds=59)

def nvd_start(date_str: str) -> str:
    """Return NVD ISO-8601 start datetime for a given day."""
    dt = parse_user_date(date_str)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

def nvd_end(date_str: str) -> str:
    """Return NVD ISO-8601 end datetime for a given day."""
    dt = parse_user_date(date_str) + timedelta(hours=23, minutes=59, seconds=59)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
