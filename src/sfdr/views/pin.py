"""
Created on Aug 7, 2011

@author: CVi
"""
import logging #@UnusedImport
def EncR_Rs(request):
    """
    EncR rescanner,
    This page simply rescans the feed, extracts the given post,
    and then checks wether or not there are any new enclosed files.
    
    @param request: Django's requeest pobject, GT used unfiltered.
    """
    from google.appengine.api import urlfetch
    from sfdr.models import Entry
    enobj = Entry.objects.get(key=request.GET['entry'])
    feedobj = enobj.feed
    result = urlfetch.fetch(feedobj.url)
    #===========================================================================
    # RSS fetched, did it return correctly?
    # in that case, let's try to make some sense out of it.
    #===========================================================================
    if result.status_code == 200:
        from sfdr.modules.feedparse import process
        items = process(result.content.lstrip())
        o = None
        #=======================================================================
        # For some reason, this is the best way i could get to do this.
        # 
        # In theory you should have the entry caught in this next loop,
        # but if it ran out of the feed you don't.
        #
        # Another scenario is that the entry changed its GUID,
        # but that would be asking for trouble
        #=======================================================================
        for i in items:
            if enobj.key == "%s->%s" % (feedobj.id, i['guid']):
                o = i
                break
        if o:
            from pickle import loads
            c = loads(feedobj.cfConf)
            #===================================================================
            # For some reason, usually upgrades, the extra data the parser gave
            # us did not make it to this point; the fix below adds empty data,
            # clean and simple.
            #===================================================================
            try:
                ose = loads(enobj.other)["cf"]
                ol = ose["l"]
            except:
                try:
                    ose = loads(enobj.other)
                    ol = ose["l"]
                    ose = {"cf":{"l":ol}}
                except:
                    logging.info("Error in loding old shit: %s" % enobj.other)
                    ol = []
                    ose = {"cf":{}}

            #===================================================================
            # Applying the EncR parser. This needs to be separated into
            # a separate subroutine to make it easier to maintain.
            #
            # API: function returning the string list.
            # 
            # TODO: Move the EncR parser into a separate subroutine.
            #===================================================================
            logging.debug("EncR parser applied")
            if c['type'] == "EncR" and c['owl']:
                l = []
                e = []
                for i in c['Fs']:
                    for j in o['enc']:
                        if i["query"] in j:
                            l.append(i["set"])
                            e.append(j)
                #===============================================================
                # OK! so far so good, now we need to do some simple stuff.
                # 1. Did we get all of them?
                # -    Not? Tell someone
                # 2. Join the lists (for later storage)
                # 3. Diff the lists (any new ones show up?)
                # 
                # TODO: Tell someone should email the owner, not just log it.
                #===============================================================
                l = set(l)
                logging.debug("l %s" % str(list(l)))
                ol = set(ol)
                logging.debug("ol %s" % str(list(ol)))
                if len(l) != len(o['enc']):
                    logging.warning("Didn't get %s" % str(list(set(o['enc']) - set(e))))
                lt = list(l | ol)
                logging.debug("%s" % str(list(lt)))
                l = list(l - ol)
                from datetime import datetime, timedelta
                from google.appengine.api.taskqueue import add
                if len(l) > 0:
                    #===========================================================
                    # Something new was found, let us do something about it
                    # 
                    # TODO: this assembler really should be it's own function.
                    #===========================================================
                    s = c['owlPre']
                    for i in l:
                        if i == l[0]:
                            s = s + i
                        elif i == l[-1]:
                            s = s + c['Sl'] + i
                        else:
                            s = s + c['So'] + i
                    s = s + c['owlPost'] + o["title"]
                    st = s
                    logging.debug("owl: %s" % (st))
                    svs = feedobj.postTo
                    if svs:
                       from sfdr.modules.post import push
                       from sfdr.models import Service
                       for s in svs:
                           svs = Service.objects.get(key=s)
                           push(svs, st, enobj.shortURL)
                    #===========================================================
                    # Now that we found one new entry, we reschedule the task
                    # to run next week.
                    #===========================================================
                    add(
                       url="/tasks/pin/encr_rs.py",
                       params={"entry":enobj.key, "count":1},
                       method="GET",
                       queue_name="longterm",
                       eta=datetime.now() + timedelta(days=7)
                      )
                    #===========================================================
                    # Important! Store the data back or we'll get
                    # a infinite loop.
                    #===========================================================
                    from pickle import dumps
                    ose["cf"]["l"] = lt
                    enobj.other = dumps(ose)
                    enobj.save()
                else:
                    #===========================================================
                    # Reschedule, 3 times if 3 weeks goes by without any
                    # new enclosed files, stop rescheduling.
                    #===========================================================
                    if ("count" not in request.GET) or (int(request.GET["count"]) < 4):
                        if "count" not in request.GET:
                            count = 1
                        else:
                            count = int(request.GET["count"]) + 1
                        add(
                            url="/tasks/pin/encr_rs.py",
                            params={"entry":enobj.key, "count":count},
                            method="GET",
                            queue_name="longterm",
                            eta=datetime.now() + timedelta(days=7)
                        )
                        logging.debug("No new enclosures, trying again next week!")
                    else:
                        logging.debug("No new enclosures, and timer ran out, Quiting!")
            else:
                logging.warning("No config on EncR cf")
    #===========================================================================
    # In any case, send success to the task queue API.
    #===========================================================================
    from django.http import HttpResponse
    return HttpResponse()
