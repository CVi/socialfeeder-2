"""
Created on 12. juni 2011

@author: "Christoffer Viken"
"""
import logging #@UnresolvedImport
import settings

def feed(request):
    """
    Fetches feeds and looks for new posts;
    there is not a lot in the way of error catching, may have to be fixed.
    
    This is theoretically the page that causes the most CPU usage
    in the entire application, so optimization is needed
    
    DODO: Add more error fetching
    
    No input sanitizing is done here, this is a background task anyway.
    
    @param request: Djangos request object, GET is used unfiltered, 
    """
    from google.appengine.api import urlfetch
    from sfdr.models import Feed, Entry
    feedobj = Feed.objects.get(id=request.GET['feed'])

    result = urlfetch.fetch(feedobj.url)
    if result.status_code == 200:
        from sfdr.modules.feedparse import process, itemTester
        items = process(result.content.lstrip())
        logging.debug("loaded %s items from RSS-feed %s" % (len(items), feedobj.name))
        tester = itemTester()
        u = tester.process(feedobj, items)
        del items
        from datetime import datetime, timedelta
        from google.appengine.api.taskqueue import add, TombstonedTaskError, TaskAlreadyExistsError #@UnresolvedImport
        now = datetime.now()
        if u:
            from sfdr.modules.feedparse import cfWrapper
            logging.debug("U loaded %s" % len(u))
            logging.debug("Strange %s " % str(u))
            cf = cfWrapper()
            for i in u:
                (i, cfo) = cf.parse(i, feedobj)
                from pickle import dumps
                if not i['date']:
                    now = now + timedelta(seconds=1)
                    i['date'] = now
                    logging.debug("Added a second to : \"%s\"" % i['guid'])
                try:
                    cfd = cfo["cfd"]
                except:
                    cfd = None
                e = Entry(
                          feed=feedobj,
                          key="%s->%s" % (feedobj.id, i['guid']),
                          date=i['date'],
                          guid=i['guid'],
                          title=i['title'],
                          url=i['link'],
                          summary=i['summary'],
                          other=dumps({"cf":cfd})
                         )
                e.save()
                logging.debug("Added post \"%s\"" % i['guid'])
                try:
                    from hashlib import sha1
                    add(
                        url="/tasks/post.py",
                        name=sha1(e.key).hexdigest() + settings.TQWOKEY,
                        params={"post":str(e.key)},
                        method="GET",
                        queue_name="posts"
                       )
                    if cfo and "call" in cfo:
                        logging.debug("Adding OWL call")
                        add(
                            url=cfo["call"],
                            params={"entry":e.key},
                            method="GET",
                            queue_name="longterm",
                            eta=datetime.now() + timedelta(days=7)
                           )
                except TaskAlreadyExistsError: #@UnusedVariable
                    logging.error("Existing task encountered: " + str(i))
                except TombstonedTaskError:
                    logging.error("Error occurred, TombstonedTask: " + str(i))
        feedobj.lastCk = datetime.now()
        if feedobj.nextCk < datetime.now() + timedelta(minutes=5):
            logging.debug("Resceduling now")
            feedobj.nextCk = datetime.now() + timedelta(minutes=30)
            add(
                url="/tasks/feeds/fetch.py",
                params={"feed":str(request.GET['feed'])},
                queue_name="feed-burns",
                method="GET",
                eta=datetime.now() + timedelta(minutes=30)
               )
        else:
            logging.debug("Not Resceduling Now: %s, nextCheck: %s  %s" %
                          (
                           str(datetime.now() + timedelta(minutes=5)),
                           str(feedobj.nextCk),
                           (feedobj.nextCk < datetime.now() + timedelta(minutes=5)))
                          )
        feedobj.save()
        from django.http import HttpResponse
        return HttpResponse()
    else:
        logging.error("Unknown Error!")
        logging.error("Debug: %s" % result)
        from django.http import HttpResponseServerError
        return HttpResponseServerError()

def orophanedFeeds(request): #@UnusedVariable
    """
    Sometimes a bug occurs and a feed is not resceduled, (preddy rare nowdays)
    This page finds those feeds and rescedules them.
    
    @param request: Djangos request object, not used.
    """
    from datetime import datetime, timedelta
    from sfdr.models import Feed
    last = datetime.now() - timedelta(minutes=15)
    res = Feed.objects.filter(nextCk__gt=last).order_by("nextCk")[:10]
    if len(res) >= 1:
        from google.appengine.api.taskqueue import add, TaskAlreadyExistsError #@UnresolvedImport
        for i in res:
            try:
                add(
                    url="/tasks/feeds/fetch.py",
                    params={"feed":str(i.id)},
                    method="GET",
                    queue_name="feed-burns"
                   )
            except TaskAlreadyExistsError, e: #@UnusedVariable
                pass
    from django.http import HttpResponse
    return HttpResponse()

def orophanedPosts(request): #@UnusedVariable
    """
    Sometimes a bug occurs and a post is not posted, (happens occasionally)
    this page finds posts it suspects are forgoten and tries to rescedule them.
    
    @param request: Djangos request object, not used.
    """
    from sfdr.models import Entry
    res = Entry.objects.filter(posted=None)[:10]
    if len(res) >= 1:
        from google.appengine.api.taskqueue import add, TaskAlreadyExistsError, TombstonedTaskError #@UnresolvedImport
        for i in res:
            try:
                from hashlib import sha1
                add(
                    url="/tasks/post.py",
                    name=sha1(i.key).hexdigest() + settings.TQWOKEY,
                    params={"post":str(i.key)},
                    method="GET",
                    queue_name="posts"
                   )
            except TaskAlreadyExistsError: #@UnusedVariable
                logging.warning("Existing task encountered!")
            except TombstonedTaskError: #@UnusedVariable
                logging.warning("Toombstoned task encountered!")
    from django.http import HttpResponse
    return HttpResponse()

def post(request):
    """
    Task to actually preform the posting of an item...
    Currently it only supports twitter, but it is designed with multi-service in mind.
    
    @param request: Djangos request object, GET data used unfiltered.
    """
    from sfdr.models import Entry
    from datetime import datetime
    entryKey = request.GET['post']
    entryObj = Entry.objects.get(key=entryKey)
    if not entryObj.posted:
        feed = entryObj.feed
        shortener = feed.urlShortener
        if not entryObj.shortURL:
            from sfdr.modules.shorten import parser as shorten
            entryObj.shortURL = shorten(shortener, entryObj.url)
        svs = feed.postTo
        if svs:
            from sfdr.modules.post import parser as postparse
            from sfdr.models import Service
            for s in svs:
                svs = Service.objects.get(key=s)
                postparse(feed, svs, entryObj)
        entryObj.posted = datetime.now()
        entryObj.save()
    from django.http import HttpResponse
    return HttpResponse()

def calcTimerProfile(request): #@UnusedVariable
    """
    This is actually not in use yet.
    The Idea is that feeds that only post on I.E. tuesday morning
    only need to be checked on Tuesday mornings.
    
    @param request: Djangos request object, not used
    """
    from sfdr.models import Feed, Entry
    from datetime import datetime, timedelta
    from pickle import dumps
    from sfdr.modules.rstimer import wdpG
    d = datetime.now() - timedelta(days=30)
    Fo = Feed.objects.filter(lastTimerCk__gt=d).order_by("lastTimerCk").get()
    if Fo:
        es = Entry.objects.filter(feed=Fo).order_by("-date").fetch(40)
        if len(es) < 20:
            Fo.lastTimerCk = datetime.now()
            Fo.save()
            logging.info("Not enough entries (%s/20) on feed to make profile: %s" % (str(len(es)), str(Fo.key())))
        else:
            data = []
            for e in es:
                data.append(e.date)
            del es
            wdhp = wdpG(data)
            do = dumps(wdhp)
            Fo.timerProfile = do
            Fo.timerEngine = "WDC"

    logging.info("No feeds found, skipping run.")
    from django.http import HttpResponse
    return HttpResponse()
