from datetime import datetime, timedelta


def genDate(modifier: int = 0, date: datetime = datetime.now()) -> datetime:
    date += timedelta(days=modifier)
    if date.hour > 12:
        date += timedelta(days=1)
    if date.weekday() > 4:
        date += timedelta(days=(7-date.weekday()))
    return date


def getMonday(date: datetime = datetime.today()) -> datetime:
    if date.weekday() >= 5:
        date += timedelta(days=(7 - date.weekday()))
    else:
        date -= timedelta(days=(date.weekday()))
    return date


def multiMonth(date: datetime) -> bool:
    monday = date - timedelta(days=(date.weekday()))
    friday = date + timedelta(days=(4-date.weekday()))

    if monday.month == friday.month:
        return False
    return True
