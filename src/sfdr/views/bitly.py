"""
Created on 27. mai 2011

@author: "Christoffer Viken"
"""
from django.http import HttpResponseRedirect

def redirect(request):
    """
    Preforms the bit.ly redirect for authentication
    
    @param request: Djangos request object
    """
    if request.user.is_authenticated():
        from sfdr.modules.bitly import connect
        import settings
        con = connect(settings.BITLY_PUB, settings.BITLY_PRI, settings.BITLY_CBK)
        red = con.redirect()
        return HttpResponseRedirect(red)
    else:
        return HttpResponseRedirect("/session/login.html")

def callback(request):
    """
    Gets the bit.ly user information and stores it in the database.
    
    @param request: Djangos request object
    """
    if request.user.is_authenticated():
        from sfdr.modules.bitly import connect
        import settings
        con = connect(settings.BITLY_PUB, settings.BITLY_PRI, settings.BITLY_CBK)
        data = con.verify(request.GET)
        from sfdr.models import Shortener
        service = Shortener(
                            key="%s:%s@%s" % (request.user.id, data['login'], "bitly"),
                            user=request.user,
                            shortener="bitly",
                            userName=data['login'],
                            pubKey=str(data['apiKey']),
                            priKey=str(data['access_token'])
                            )
        service.save()
        return HttpResponseRedirect("/dashboard.html")
    else:
        return HttpResponseRedirect("/session/login.html")
