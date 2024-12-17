import datetime

import dateutil.tz


def get_datetime_msk_tz(
    dt: datetime.datetime | str | None = None,
) -> datetime.datetime:
    dt = dt or utcnow()
    if isinstance(dt, str):
        if dt.lower()[-1] == 'z':
            dt = dt[:-1]
        dt = datetime.datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt.astimezone(dateutil.tz.gettz('Europe/Moscow')).replace(tzinfo=None)


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=datetime.timezone.utc)
