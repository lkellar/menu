from datetime import datetime, timedelta
from collections import OrderedDict
from smtplib import SMTP_SSL
from email.mime.text import MIMEText

def genDate(modifier: int = 0, date: datetime = None) -> datetime:
    if not date:
        date = datetime.now()
    date += timedelta(days=modifier)
    if date.hour > 12:
        date += timedelta(days=1)
    if date.weekday() > 4:
        date += timedelta(days=(7-date.weekday()))
    return date


def genDateClasses(data: dict, date: datetime, entry: str) -> dict:
    keys = sorted(data.keys())
    menus = OrderedDict({i: data[i] for i in keys})

    if date.strftime('%Y-%m-%d') not in keys:
        for i in range(0, 5):
            date += timedelta(days=1)
            if date.strftime('%Y-%m-%d') in keys:
                break

    if entry == 'first':
        first = next(iter(menus))
        current = {first: menus[first]}
        menus.pop(first)
        before, after = [], menus
    elif entry == 'last':
        last = menus.popitem()
        current = {last[0]: last[1]}
        before, after = menus, []
    else:
        today = date.strftime('%Y-%m-%d')
        before, current, after = {}, {}, {}
        for i in menus:
            if i < today:
                before[i] = menus[i]
            elif i == today:
                current[i] = menus[i]
            elif i > today:
                after[i] = menus[i]

    return {'before': before, 'current': current, 'after': after}


def getMonday(date: datetime = datetime.today()) -> datetime:
    if date.weekday() >= 5:
        date += timedelta(days=(7 - date.weekday()))
    else:
        date -= timedelta(days=(date.weekday()))
    return date


def multiMonth(date: datetime) -> bool:
    monday = date - timedelta(days=(datetime.today().weekday()))
    friday = date + timedelta(days=(4-date.weekday()))

    if monday.month == friday.month:
        return False
    return True


# Credit for below function goes to Stack Overflow User simleo
def monthlist_fast(dates):
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    total_months = lambda dt: dt.month + 12 * dt.year

    mlist = []
    for tot_m in range(total_months(start)-1, total_months(end)):
        y, m = divmod(tot_m, 12)
        mlist.append(datetime(y, m+1, 1).strftime('%Y-%m'))
    return mlist



def genNumber(num: int) -> str:
    lastDigit = num % 10

    if lastDigit == 1:
        return f'{num}st'
    elif lastDigit == 2:
        return f'{num}nd'
    elif lastDigit == 3:
        return f'{num}rd'
    else:
        return f'{num}th'


def emailAdmin(config: dict, titles: list, menuChoice: str):
    # Sends an email to an admin alerting them that their selected menu doesn't exist
    formattedTitles = '\n'.join(titles)
    msg = MIMEText(f'Selected menu "{menuChoice}" is unavailable. Available menus are:\n{formattedTitles}')

    msg['Subject'] = 'Menu Choice is unavailable!🔥'
    msg['To'] = config['to']
    msg['From'] = config['from']

    with SMTP_SSL(config['server'], port=config['port']) as s:
        s.login(config['username'], config['password'])
        s.send_message(msg, from_addr=config['from'], to_addrs=config['to'])
