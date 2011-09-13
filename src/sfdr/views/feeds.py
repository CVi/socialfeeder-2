"""
Created on 18. mars 2011

@author: "Christoffer Viken"
"""
from django.http import HttpResponseRedirect
import logging

def add(request):
    """
    This page just displays the add-a-new-feed-form
    @param request: Djangos request object
    """
    if request.user.is_authenticated():
        from django.shortcuts import render_to_response
        from sfdr.forms import feedForm
        from sfdr.models import Shortener
        form = feedForm(Shortener.objects.filter(user=request.user))
        return render_to_response("feedadd.html", {"action":"/feeds/put.py", "form":form })
    else:
        return HttpResponseRedirect("/session/login.html")

def put(request):
    """
    Stores the data submitted from the form, or displays an error message.
    @param request: Djangos request object
    """
    if request.user.is_authenticated():
        #TODO: Convert form to AJAX
        from sfdr.forms import feedForm
        from sfdr.models import Shortener
        form = feedForm(Shortener.objects.filter(user=request.user), request.POST)
        if form.is_valid():
            from sfdr.models import Feed
            f = Feed(
                    user=request.user,
                    name=form.cleaned_data['nm'],
                    url=form.cleaned_data['fd'],
                    urlShortener=form.cleaned_data['snr'],
                    postType=form.cleaned_data['fmt'],
                    preText=str(form.cleaned_data['pre']),
                    postText=str(form.cleaned_data['post']),
                    filter=str(form.cleaned_data['fi']),
                    filterOn=str(form.cleaned_data['fo']),
                    )
            f.save()
            logging.debug("Added Feed \"" + form.cleaned_data['nm'] + "\" to list")
            from google.appengine.api.taskqueue import add #@UnresolvedImport
            add(
                url="/tasks/feeds/fetch.py",
                params={"feed":str(f.id)},
                method="GET",
                queue_name="feed-burns"
            )
        else:
            from django.shortcuts import render_to_response
            return render_to_response("feedadd.html", {"form":form})
            logging.debug("Unsuccessful reg because:" + str(form.errors))
        return HttpResponseRedirect("/dashboard.html")
    else:
        return HttpResponseRedirect("/session/login.html")

def edit(request, feed=None):
    """
    Displays the editing form for a feed, prepopulated with the data from database.
    
    @param request: Django's request object
    @param feed: the ID of the feed to be edited.
    """
    if request.user.is_authenticated():
        from sfdr.models import Feed
        from sfdr.forms import feedForm
        feed = int(feed)
        Fo = Feed.objects.get(pk=feed, user=request.user)
        if not Fo:
            from django.http import Http404
            raise Http404
        else:
            from sfdr.models import Shortener, Service
            from django.shortcuts import render_to_response
            from settings import cfMODS
            sva = []
            svr = []
            svs = Service.objects.filter(user=request.user)
            for s in svs:
                if s.key in Fo.postTo:
                    svr.append(s)
                else:
                    sva.append(s)
            init = {
                    "nm":Fo.name,
                    "fd":Fo.url,
                    "snr":Fo.urlShortener,
                    "fmt":Fo.postType,
                    "feed":feed,
                    "pre":Fo.preText,
                    "post":Fo.postText,
                    "fo":Fo.filterOn,
                    "fi":Fo.filter,
                    "cfM":Fo.cfMod
                    }
            form = feedForm(Shortener.objects.filter(user=request.user), initial=init)
            cfL = (Fo.cfMod != "None" and Fo.cfMod != None and Fo.cfMod in cfMODS)
            return render_to_response(
                                      "feedadd.html",
                                      {
                                       "action":"/feeds/store.py",
                                       "id":feed,
                                       "form":form,
                                       "sva":sva,
                                       "svr":svr,
                                       "cfL":cfL,
                                       "dbg":Fo.cfMod
                                      }
                                     )
    else:
        return HttpResponseRedirect("/session/login.html")

def filterMod(request, feed=None):
    """
    Editor for content filter module configurations.
    This one in fully AJAX.
    
    @param request: Djangos request object
    @param feed: the ID of the feed whose CF modul you waant to edit.
    """
    if request.user.is_authenticated():
        from sfdr.models import Feed
        feed = int(feed)
        try:
            Fo = Feed.objects.get(id=feed, user=request.user)
        except:
            from django.http import Http404
            raise Http404
        import settings
        if Fo.cfMod in settings.cfMODS:
            from django.shortcuts import render_to_response
            return render_to_response("modules/cf.html", {"feed":Fo})
    else:
        return HttpResponseRedirect("/session/login.html")

def store(request):
    """
    Saves the new feed information to database
    
    @param request: Djangos request object.
    """
    if request.user.is_authenticated():
        from sfdr.forms import feedForm
        from sfdr.models import Shortener
        form = feedForm(Shortener.objects.filter(user=request.user), request.POST)
        if form.is_valid() and form.cleaned_data['fd']:
            from sfdr.models import Feed
            fid = form.cleaned_data['feed']
            try:
                Fo = Feed.objects.get(id=fid)
            except:
                from django.http import Http404
                raise Http404
            Fo.name = form.cleaned_data['nm']
            Fo.url = form.cleaned_data['fd']
            Fo.preText = str(form.cleaned_data['pre'])
            Fo.postText = str(form.cleaned_data['post'])
            Fo.postType = form.cleaned_data['fmt']
            Fo.filter = str(form.cleaned_data['fi'])
            Fo.filterOn = str(form.cleaned_data['fo'])
            Fo.cfMod = str(form.cleaned_data['cfM'])
            Fo.save()
            return HttpResponseRedirect("/dashboard.html")
        else:
            from django.shortcuts import render_to_response
            return render_to_response("feedadd.html", {"form":form, })
        logging.debug("Unsuccessful edit because:" + str(form.errors))
        return HttpResponseRedirect("/feeds/edit/" + request.POST['fd'] + ".py")
    else:
        return HttpResponseRedirect("/session/login.html")

def sva(request):
    """
    Add a social media service to the feed
    
    @param request: Djangos request object
    """
    if request.user.is_authenticated():
        #TODO: Service-to-feed adding REALLY needs to be AJAXified        
        from sfdr.models import Feed, Service
        feed = int(request.POST['fd'])
        svs = request.POST['svs']
        try:
            So = Service.objects.get(user=request.user, key=svs)
            Fo = Feed.objects.get(id=feed, user=request.user)
        except:
            from django.http import Http404
            raise Http404
        if Fo and So and svs not in Fo.postTo:
            Fo.postTo.append(svs)
            Fo.save()
        return HttpResponseRedirect("/feeds/edit/%s.py" % feed)
    else:
        return HttpResponseRedirect("/session/login.html")

def svr(request):
    """
    Removes a social media service from the feed
    
    @param request: Djangos request object
    """
    if request.user.is_authenticated():
        #TODO: Service-from-removal adding REALLY needs to be AJAXified
        from sfdr.models import Feed
        feed = int(request.POST['fd'])
        svs = request.POST['svs']
        try:
            Fo = Feed.objects.get(id=feed, user=request.user)
        except:
            from django.http import Http404
            raise Http404
        if Fo and svs in Fo.postTo:
            Fo.postTo.remove(svs)
            Fo.save()
        return HttpResponseRedirect("/feeds/edit/%s.py" % feed)
    else:
        return HttpResponseRedirect("/session/login.html")
