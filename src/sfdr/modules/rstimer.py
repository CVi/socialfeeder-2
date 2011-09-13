"""
Created on 29. mars 2011

@author: "Christoffer Viken"
"""
def wdpG(data):
    """
    Weekday profile, Generator.
    @param data: Training dataset (list of datetime objects)
    @return: Rescheduler profile
    """
    wdp = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}
    for d in data:
        wdp[d.weekday()][d.hour] = True
    del data
    wdhp = {0:(), 1:(), 2:(), 3:(), 4:(), 5:(), 6:()}
    for k, v in wdp.iteritems():
        last = -1
        for x in range(0, 23):
            if last < x:
                if x in v:
                    r = x
                    while r + 1 in k: r = r + 1
                    wdhp[k].append((x, r))
                    last = r
    return wdhp

def wdndpG(data):
    """
    Weekday "No Post" profile, Generator.
    @param data: Training dataset (list of datetime objects)
    @return: Rescheduler profile
    """
    wdp = {0:False, 1:False, 2:False, 3:False, 4:False, 5:False, 6:False}
    for d in data:
        wdp[d.weekday()] = True
    return wdp

def wdpC(profile, tag="FS", fi=False):
    """
    Weekday profile, Rescheduler.
    
    @param profile: Resceduling profile
    @param tag: FS="Fresh Start";PS="Period Scan";ES="Extended Scan";PE="Period End"
    @param fi: Bool, post found yet?
    @return: datetime for next check, string with message for next rescheduler
    """
    from datetime import date, time, timedelta, datetime
    today = date.today()
    wdt = today.weekday()
    dtn = datetime.now()
    next = None
    now = time(hour=dtn.hour, minute=dtn.minute, second=dtn.second)
    if tag == "FS" or tag == "PE" or (tag == "ES" and fi):
        pd = profile[wdt]
        for h in pd:
            start = time(hour=h[0])
            end = time(hour=h[1] + 1)
            if start > now:
                next = datetime.combine(today, start)
                tag = "PS"
                break
            if end > now:
                next = datetime.combine(today, end)
                tag = "PE"
        if not next:
            day = wdt + 1
            r = False
            while not (day == (wdt + 1) and r):
                r = True
                if day >= 7:
                    day = 0
                if len(profile[day]) >= 1:
                    t = time(hour=profile[day][0][0])
                    ds = day - wdt
                    if ds < 0:
                        ds = ds + 7
                    td = timedelta(days=ds)
                    date = today + td
                    next = datetime.combine(date, t)
                    tag = "PS"
                    break
                day = day + 1
        if not next:
            next = dtn + timedelta(hours=2, minutes=30)
            tag = "FS"
    elif tag == "PS" and fi:
        pd = profile[wdt]
        for h in pd:
            start = time(hour=h[0])
            end = time(hour=h[1] + 1)
            if start <= now and end > now:
                next = datetime.combine(today, end)
                tag = "PE"
                break
        else:
            next = dtn + timedelta(hours=1)
            tag = "PE"
    elif (tag == "PS" or tag == "ES") and not fi:
        day = profile[wdt]
        for p in day:
            start = time(hour=p[0])
            end = time(hour=p[1] + 1)
            if start <= now and end > now:
                pl = p[0] - p[1]
                md = 10 + (5 * pl)
                next = dtn + timedelta(minutes=md)
                tag = "PS"
                break
        if not next:
            from random import randrange
            md = randrange(30, 59, 1)
            next = dtn + timedelta(minutes=md)
            tag = "ES"
    else:
        next = dtn + timedelta(hours=1)
        tag = "FS"
    return next, tag
