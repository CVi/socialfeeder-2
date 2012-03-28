"""
Created on 21. mars 2011

@author: "Christoffer Viken"
"""
import logging #@UnresolvedImport

def push(service, text, link):
    """
    Wrapper for the social network services for posting.
    
    @param service: service model instance
    @param text: text to post
    @param link: link to post
    """
    def twitter(service, text, link):
        from sfdr.modules.twitter import api
        import settings
        twitter = api(settings.TWITTER_PUB, settings.TWITTER_PRI, service.pubKey, service.priKey)
        logging.debug("Tweeting now to %s; link: \"%s\", ttl: \"%s\"" % (service.key, link, text))
        twitter.push(text, link)

    def _noOp(service, text, link): #@UnusedVariable
        logging.error("Strange \"%s\" is not known" % service.service)
        pass

    dset = {"twitter":twitter}
    dset.get(service.service, _noOp)(service, text, link)

def parser(feed, service, entry):
    """
    Bad name, sorry to be fixed later
    wrapper to preform a post of a RSS entry
    
    TODO: Rename modules.post.parser to something else
    
    @param feed: feed model object (for settings)
    @param service: service model object
    @param entry: entry model object
    """
    def twitter(service, link, title, desc):
        title = unicode(title, errors='ignore')
        from sfdr.modules.twitter import api
        import settings
        twitter = api(settings.TWITTER_PUB, settings.TWITTER_PRI, service.pubKey, service.priKey)
        logging.debug("Tweeting now to %s; link: \"%s\", ttl: \"%s\"" % (service.key, link, str(title.encode('ascii', 'ignore'))))
        twitter.post(link, title, desc, feed.preText, feed.postText)

    def _noOp(service, link, title, desc, pre, post): #@UnusedVariable
        logging.error("Strange \"%s\" is not known" % service.service)
        pass

    dset = {"twitter":twitter}
    link = entry.shortURL
    if feed.postType == "TL" or feed.postType == "TDL":
        title = entry.title
    else:
        title = None
    if feed.postType == "DL" or feed.postType == "TDL":
        desc = entry.summary
    else:
        desc = None
    dset.get(service.service, _noOp)(service, link, title, desc)
