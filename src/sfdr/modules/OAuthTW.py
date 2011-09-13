"""
Created on 13. mars 2011

@author: "Christoffer Viken"
"""

from google.appengine.ext import db

class OAuthTW(db.Model):
    """
    Old leftover from v1.0
    Temporary Oauth token model 
    """
    secret = db.BlobProperty()
    date = db.DateProperty(auto_now_add=True)
    service = db.StringProperty()
