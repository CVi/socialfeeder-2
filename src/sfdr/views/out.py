"""
Created on 26. mai 2011

@author: "Christoffer Viken"
"""

def frontpage(request):
    """
    Redirects the user to their dashboard if they are logged in,
    shows the static frontpage otherwise.
    
    @param request: Django's request object; not used.
    """
    if request.user.is_authenticated():
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/dashboard.html')
    else:
        from django.shortcuts import render_to_response
        return render_to_response('frontpage.html', {})
