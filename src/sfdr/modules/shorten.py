"""
Created on 20. mars 2011

@author: "Christoffer Viken"
"""

def parser(shortener, url):
    """
    Wrapper around the different APIs for URL shorteners
    
    @param shortener: Shortener model object
    @param url: the actual URL to shorten
    """
    def bitly(shortener, url):
        from sfdr.modules.bitly import api
        bitly = api(shortener.userName, shortener.priKey, shortener.pubKey)
        return bitly.shorten(url)

    def empty(shortener, url): #@UnusedVariable
        return url

    dset = {"bitly":bitly}
    return dset.get(shortener.shortener, empty)(shortener, url)
