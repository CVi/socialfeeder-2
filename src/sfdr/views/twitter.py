"""
Created on 27. mai 2011

@author: "Christoffer Viken"
"""
from django.http import HttpResponseRedirect

def redirect(request): #@UnusedVariable
    """
    Redirects the user to the twitter auth page,
    in reality just a thin wrapper around the twitter modules connect.
    @param request: Django's request object, not used here.
    """
    if request.user.is_authenticated():
        from sfdr.modules.twitter import connect
        import settings
        con = connect(settings.TWITTER_PUB, settings.TWITTER_PRI)
        red = con.redirect(settings.TWITTER_CBK)
        return HttpResponseRedirect(red)
    else:
        return HttpResponseRedirect("/session/login.html")

def callback(request): #@UnusedVariable
    """
    When the user returns, get the auth info and save the data.
    @param request: Django's request object, not used here.
    """
    if request.user.is_authenticated():
        from sfdr.modules.twitter import connect
        import settings
        con = connect(settings.TWITTER_PUB, settings.TWITTER_PRI)
        data = con.verify(request.GET)
        from sfdr.models import Service
        service = Service(
                          key="%s:%s@%s" % (request.user.id, data['screen_name'], "twitter"),
                          user=request.user,
                          service="twitter",
                          userName=data['screen_name'],
                          avatar=str(data['profile_image_url']),
                          pubKey=str(data['oauth_token']),
                          priKey=str(data['oauth_token_secret'])
                          )
        service.save()
        return HttpResponseRedirect("/dashboard.html")
    else:
        return HttpResponseRedirect("/session/login.html")
