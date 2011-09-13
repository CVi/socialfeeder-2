"""
Created on 27. mai 2011

@author: "Christoffer Viken"
"""
from sfdr.modules.OAuthTW import OAuthTW
from lib.oauth2 import Consumer, Token, Client
import logging #@UnusedImport

class connect:
    """
    Twitter connection establisher
    
    Provides an API to preform oAuth authentication requests to twitter.
    """
    authorize_url = 'https://twitter.com/oauth/authorize'
    request_token_url = 'https://twitter.com/oauth/request_token'
    access_token_url = 'https://twitter.com/oauth/access_token'
    userinfo_url = 'https://api.twitter.com/1/account/verify_credentials.json'

    def __init__(self, pub, pri):
        """
        @param pub: Applications Public key
        @param pri: Applications private key
        """
        self.consumer = Consumer(key=pub, secret=pri)

    def redirect(self, callback):
        """
        Initiates a oAuth authentication request.
        @param callback: The callback URL
        @return: The URL to redirect the user to
        """
        from lib.urlparse import parse_qsl
        from urllib import urlencode #@UnresolvedImport
        self.client = Client(self.consumer)
        resp, content = self.client.request(self.request_token_url, "POST", body=urlencode({"oauth_callback": callback}))
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(parse_qsl(content))
        OAuthTW(
                key_name=request_token['oauth_token'],
                secret=request_token['oauth_token_secret'],
                service="twitter"
                ).put()
        return "%s?oauth_token=%s" % (self.authorize_url, request_token['oauth_token'])

    def verify(self, req):
        """
        Verifies returned user and extracts user information
        @param req: the GET data from the page call.
        @return: The users information
        @rtype: dict
        """
        from lib.urlparse import parse_qsl
        from django.utils import simplejson as json
        auth_token = req["oauth_token"]
        auth_verifier = req["oauth_verifier"]
        dataset = OAuthTW.get_by_key_name(auth_token)
        token = Token(auth_token, dataset.secret)
        token.set_verifier(auth_verifier)
        self.client = Client(self.consumer, token)
        resp, content = self.client.request(self.access_token_url, "POST") #@UnusedVariable
        auth = dict(parse_qsl(content))

        token = Token(auth['oauth_token'], auth['oauth_token_secret'])
        self.client = Client(self.consumer, token)
        resp, content = self.client.request(self.userinfo_url, "GET") #@UnusedVariable
        info = json.loads(content)
        info.update(auth)
        dataset.delete()
        return info

class api:
    """
    Twitter REST API interface
    """
    update_url = "https://api.twitter.com/1/statuses/update.json"

    def __init__(self, pub, pri, auth_token, auth_token_secret):
        """
        @param pub: Applications public key
        @param pri: Applications private key
        @param auth_token: Users oAuth tooken
        @param auth_token_secret: Users oAuth token secretm
        """
        self.consumer = Consumer(key=pub, secret=pri)
        self.token = Token(key=auth_token, secret=auth_token_secret)
        self.client = Client(self.consumer, token=self.token)
        self.pub = pub
        self.ato = auth_token

    def post(self, link, title=None, desc=None, pre=None, post=None):
        """
        Post an RSS object to twitter, formats and auto-crops description.
        
        @param link: Shortened link to post
        @param title: Entry title
        @param desc: Entry description
        @param pre: Text in beginning of tweet
        @param post: Text at end of tweet 
        @return True
        """
        from urllib import urlencode
        if title and desc:
            if not pre: pre = ""
            if not post: post = ""
            title = title.strip()
            link = link.strip()
            dl = 137 - len(title) - len(link) - len(pre) - len(post)
            if len(desc) > dl:
                desc = desc[:dl - 4]
                desc = desc.rpartition(' ')[0] + "..."
            out = pre + title + " - " + desc + " " + link + post
        elif title and not desc:
            if not pre: pre = ""
            if not post: post = ""
            title = title.strip()
            link = link.strip()
            dl = 136 - len(title) - len(link) - len(pre) - len(post)
            out = pre + title + " " + link + post
        elif not title and desc:
            if not pre: pre = ""
            if not post: post = ""
            link = link.strip()
            dl = 139 - len(link)
            if len(desc) > dl:
                desc = desc[:dl - 4]
                desc = desc.rpartition(' ')[0] + "..."
            out = desc + " " + link

        params = {
                   "status":out
                   }
        params = urlencode(params)
        resp, content = self.client.request(self.update_url, method="POST", body=params) #@UnusedVariable
        return True

    def push(self, text, link):
        """
        Tweets a string + a link
        
        @param text: Text string to tweet
        @param link: Link to tweet
        """
        from urllib import urlencode
        if 137 - len(link) < len(text):
            text = text[:133 - len(link)]
            text = text.rpartition(' ')[0] + "..."
        out = text + " " + link
        params = {"status":out}
        params = urlencode(params)
        resp, content = self.client.request(self.update_url, method="POST", body=params) #@UnusedVariable
        return True
