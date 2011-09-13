"""
Created on 18. mai 2011

@author: "Christoffer Viken"
"""
import logging

def cfStore(request, feed=None):
    """
    Stores Content filter configuration to database
    @param request: Djangos request object
    @param feed: The ID of the feed whose configuration you want to store.
    """
    if request.user.is_authenticated():
        from sfdr.models import Feed
        logging.debug("OK, Feed: %s Data is: %s " % (feed, request.POST["data"]))
        feed = int(feed)
        try:
            Fo = Feed.objects.get(id=feed, user=request.user)
        except:
            from django.http import Http404
            raise Http404
        from django.utils.simplejson import loads
        from pickle import dumps
        from django.http import HttpResponse
        data = loads(request.POST["data"])
        Fo.cfConf = dumps(data)
        Fo.save()
        return HttpResponse()
    else:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

def cfLoad(request, feed=None):
    """
    Loads content filter from database
    @param request: Djangos request object
    @param feed: The ID of the feed whose configuration we want to store
    """
    if request.user.is_authenticated():
        from sfdr.models import Feed
        feed = int(feed)
        try:
            Fo = Feed.objects.get(id=feed, user=request.user)
        except:
            from django.http import Http404
            raise Http404
        from django.utils.simplejson import dumps
        from pickle import loads
        from django.http import HttpResponse
        if Fo.cfConf:
            data = dumps(loads(Fo.cfConf))
        else:
            data = dumps(None)
        return HttpResponse(data)
    else:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
