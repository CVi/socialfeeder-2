"""
Created on 26. mai 2011

@author: "Christoffer Viken"
"""
def dashboard(request):
    """
    Displays the users dashbard
    
    @param request: Djangos request object
    """
    from django.shortcuts import render_to_response
    from django.http import HttpResponseRedirect
    if request.user.is_authenticated():
        from sfdr.models import Service, Shortener, Feed
        svs = Service.objects.filter(user=request.user)
        srs = Shortener.objects.filter(user=request.user)
        fds = Feed.objects.filter(user=request.user)
        return render_to_response("dashboard.html", {"services":svs, "shorteners":srs, "feeds":fds})
    else:
        return HttpResponseRedirect("/session/login.html")
