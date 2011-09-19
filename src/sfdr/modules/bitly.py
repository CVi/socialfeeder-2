"""
Created on 27. mai 2011

@author: "Christoffer Viken"
"""
from lib.oauth2 import Client2
import logging

class connect:
    """
    Bit.ly connector
    """
    authorize_url = "https://bit.ly/oauth/authorize"
    access_token_url = "https://api-ssl.bitly.com/oauth/access_token"
    base_url = "https://api-ssl.bitly.com/"

    def __init__(self, pub, pri, cbk):
        """
        @param pub: Application public oAuth key
        @param pri: Application private oAuth key
        @param cbk: Application callback URL
        """
        self.Client = Client2(pub, pri, self.base_url, redirect_uri=cbk)
        self.pubkey = pub
        self.callback = cbk

    def redirect(self):
        """
        Initiates an oAuth connect session and gives the address to redirect the user to.
        
        @return: url to redirect user to
        """
        return "%s?client_id=%s&redirect_uri=%s" % (self.authorize_url, self.pubkey, self.callback)

    def verify(self, req):
        """
        Verify the user and extract the keys needed to authenticate.
        
        @param req: Requests GET data
        """
        from lib.urlparse import parse_qsl
        code = req['code']
        params = {
                  "client_id":self.pubkey,
                  "client_secret":self.Client.client_secret,
                  "code":code,
                  "redirect_uri":self.callback
                  }
        resp, content = self.Client.request(self.access_token_url, method="POST", params=params) #@UnusedVariable
        data = dict(parse_qsl(content))
        return data

class api:
    """
    Interface to the bit.ly API; incomplete, containing only what is needed
    by the socialfeeder application.
    """
    shorten_url = "https://api-ssl.bitly.com/v3/shorten"
    base_url = "https://api-ssl.bitly.com/"

    def __init__(self, login, access_token, api_key):
        """
        @param login: bit.ly username
        @param access_token: bit.ly user access token
        @param api_key: bit.ly user API key
        """
        from lib.httplib2 import Http
        self.login = login
        self.access_token = access_token
        self.api_key = api_key
        self.connector = Http()

    def shorten(self, url):
        """
        Shortens an URL with the given bit.ly account
        
        @param url: URL to shorten
        @return: shortened URL, or full URL on failure
        """
        from urllib import urlencode
        data = {
                "format":"json",
                "longUrl":url,
                "login":self.login,
                "apiKey":self.api_key
                }
        resp, content = self.connector.request(self.shorten_url + "?" + urlencode(data), "GET")
        if resp['status'] == '200':
            from django.utils import simplejson as json
            info = json.loads(content)
            if str(info['status_code']) == "200":
                if info.has_key('data'):
                    return info['data']['url']
                else:
                    return info['url']
            else:
                logging.error("Bit.ly failed for some reason" + str(info))
        logging.error("Bit.ly error detected " + str(resp))
        return url
