"""
Created on 10. mars 2011

@author: "Christoffer Viken"
"""
import logging

def process(data):
    """
    Parses a feed and pipes out a dictionary
    @param data: String of RSS feed 
    """
    from datetime import datetime
    from xml.etree import ElementTree
    from email.Utils import mktime_tz, parsedate_tz
    d = ElementTree.fromstring(data)[0].findall("item")
    del data
    dset = []
    for node in d:
        date = None
        lst = list(node)
        enc = []
        for l in lst:
            if l.tag == "pubDate": date = datetime.fromtimestamp(mktime_tz(parsedate_tz(l.text)))
            elif l.tag == "title": title = l.text
            elif l.tag == "link": link = l.text
            elif l.tag == "guid": guid = l.text
            elif l.tag == "description": desc = l.text
            elif l.tag == "enclosure": enc.append(l.get("url"))
        if not title or not link or not guid or not desc:
            logging.error("For some reason a feed item screwed up" + str(lst))
        else:
            dset.append(
                        {
                         "date":date,
                         "guid":guid,
                         "link":link,
                         "summary":desc,
                         "title":title,
                         "enc":enc
                        }
                        )
    return dset

class itemTester():
    """
    Tester to test for new entries
    """
    def process(self, feed, items):
        """
        Wrapper to all the procesing engines
        
        @param feed: feed model object 
        @param items: list of items to test
        """
        engines = {
                   "date":self._dateEngine,
                   "guid":self._guidEngine
                  }
        if len(items) > 0:
            if not items[0]["date"]:
                r = self._guidEngine(feed, items)
            else:
                r = engines.get(feed.parseEngine, self._notRecognized)(feed, items)
            return self._secondaryFilterEngine(feed, r)
        else:
            r = items
    def _dateEngine(self, feed, items):
        """
        Date test engine, finds every entry newer than the last one
        Only works if entries has the date property
        
        @param feed: feed model object 
        @param items: list of items to test
        """
        from sfdr.models import Entry
        try:
            e = Entry.objects.filter(feed=feed).order_by("-date")[0]
        except IndexError:
            logging.warning("Index Error, this is bad!")
            items = self._secondaryFilterEngine(feed, items)
            current = items[1]
            for i in items:
                if i['date'] > current['date']:
                    current = i
            ret = [current]
        else:
            logging.debug("OK filtering Now: %s items" % len(items))
            ret = []
            for i in items:
                if i['date'] > e.date:
                    ret.append(i)
        ret.reverse()
        return ret

    def _guidEngine(self, feed, items):
        """
        Imperfect "by guid" test engine.
        Includes every item higher up than the last recorded GUID in the database.
        
        @param feed: feed model object 
        @param items: list of items to test
        """
        from sfdr.models import Entry
        e = Entry.objects.filter(feed=feed).order_by("-date")[0]
        ret = []
        if not e:
            items.reverse()
            ret = items[0:5]
        else:
            for i in items:
                if i["guid"] == e.guid:
                    break
                else:
                    ret.append(i)
            ret.reverse()
            ret = ret[0:5]
        return ret

    def _notRecognized(self, feed, items): #@UnusedVariable@
        """
        Dummy engine, returns everything for when filter engine is unrecognized
        
        @param feed: feed model object 
        @param items: list of items to test
        """
        return items

    def _secondaryFilterEngine(self, feed, items):
        """
        Secondary filtering engine, looks for configured text in configured field
        
        @param feed: feed model object 
        @param items: list of items to test
        """
        if items and len(items) > 0:
            logging.debug("Secondary Filter in action! Count: %s" % len(items))
            ret = []
            for i in items:
                if feed.filterOn == "TTL": f = i['title']
                elif feed.filterOn == "DSC": f = i['summary']
                elif feed.filterOn == "LNK": f = i['link']
                elif feed.filterOn == "GUID": f = i['guid']
                else:
                    logging.debug("Hmm, strange, did not understand \"%s\" as filter" % str(feed.filterOn))
                    ret.append(i)
                    continue
                if feed.filter in f:
                    logging.debug("Ok, secondary filter got it: \"%s\" in \"%s\"" % (str(feed.filter), str(f.encode('latin-1', 'ignore'))))
                    ret.append(i)
                    continue
                logging.debug("Nothing here, go on! (\"%s\" not in \"%s\")" % (feed.filter, f.encode('latin-1', 'ignore')))
            logging.debug("Secondary filter completed")
            return ret
        else:
            return items

class cfWrapper:
    """
    Conent filter wrapper, currently it actually contains all the content filters,
    but at some later point they may get separated out for optimization.
    """
    def __init__(self):
        """
        Initiator
        Asigns the property feed
        """
        self.feed = None

    def parse(self, post, feed):
        """
        The wrap layer function that loads confiiguration and excecutes the filters
        
        @param post: RSS entry (dictionary format)
        @param feed: feed model object
        """
        from sfdr.modules.mlstripper import strip_tags
        engines = {
                   "EncR":self._EncR,
                   "RegX":self._RegX,
                   "StripR":self._StripR
                   }
        post["summary"] = strip_tags(post['summary'].encode('latin-1', 'ignore'))
        post["title"] = post["title"].encode('latin-1', 'ignore')
        if feed is not self.feed:
            self.feed = feed
            if feed.cfConf:
                from pickle import loads
                self.c = loads(feed.cfConf)
            else:
                self.c = None
        return engines.get(feed.cfMod, self._none)(post)

    def _none(self, post):
        """
        Nothing done, return the data and quit
        
        @param post: RSS entry (dictionary format)
        """
        logging.debug("No cf applied")
        return (post, None)

    def _StripR(self, post):
        """
        Flickr StripR, strips out the "(...) posted a photo:" from Flickr RSS feeds.
        Actually a preconigured RegX filter

        @param post: RSS entry (dictionary format)
        """
        self.c = {
                  "type":"RegX",
                  "rt":"",
                  "ft":"",
                  "fd":r"(?P<name>[\s\S]+) posted a photo:[\s]+(?P<desc>([\S][\s\S]+){0,1})",
                  "rd":"%(desc)s"
                  }
        return self._RegX(post)

    def _RegX(self, post):
        """
        Regular expression filter.
        Takes 2 regular expressions and 2 formating strings as arguments.
        Takes the extracted values from the regular expressions and
        formats them using the formating strings. 
        
        @param post: RSS entry (dictionary format)
        """
        logging.debug("RegX parser applied")
        if self.c and self.c['type'] == "RegX":
            import sys
            try:
                import re
                try:
                    if self.c["rt"] != "" and  self.c["ft"] != "":
                        ot = self.c["rt"] % re.compile(self.c["ft"]).match(post["title"]).groupdict()
                        post["title"] = ot
                        del ot
                except:
                    pass
                try:
                    if self.c["rd"] != "" and  self.c["fd"] != "":
                        od = self.c["rd"] % re.compile(self.c["fd"]).match(post["summary"]).groupdict()
                        post["summary"] = od
                        del od
                except:
                    pass
                return (post, None)
            except:
                logging.warning("Config problem on RegX cf: %s" % sys.exc_info()[0])
                return post

    def _EncR(self, post):
        """
        Enclosures identifier filter.
        Looks trough the enclosed file paths for a list of strings,
        upon finding them it lists them and appends the resulting string to
        eighter the title or the description. 
        
        @param post: RSS entry (dictionary format)
        """
        logging.debug("EncR parser applied")
        if self.c and self.c['type'] == "EncR":
            try:
                l = []
                for i in self.c['Fs']:
                    for j in post['enc']:
                        if i["query"] in j:
                            l.append(i["set"])
                l = list(set(l))
                s = self.c['pre']
                t = post['title']
                if len(l) > 0:
                    for i in l:
                        if i == l[0]:
                            s = s + i
                        elif i == l[-1]:
                            s = s + self.c['Sl'] + i
                        else:
                            s = s + self.c['So'] + i
                    s = s + self.c['post']
                    st = s
                    logging.debug("%s -*- %s  %s" % (st, self.c['aTo'], self.c['aPo']))
                    if self.c['aTo'] == "T":
                        if self.c['aPo'] == "B":
                            post['title'] = s + post['title']
                        elif self.c['aPo'] == "A":
                            post['title'] = post['title'] + s
                        elif self.c['aPo'] == "R":
                            post['title'] = s
                    elif self.c['aTo'] == "D":
                        if self.c['aPo'] == "B":
                            post['summary'] = s + post['summary']
                        elif self.c['aPo'] == "A":
                            post['summary'] = post['summary'] + s
                        elif self.c['aPo'] == "R":
                            post['summary'] = s
                    logging.debug("EncR parser got It %s" % s);
                elif len(post['enc']) > 0:
                    from google.appengine.api import mail
                    mail.send_mail(sender="Socialfeeder app <christoffer.viken+sfdr@gmail.com>",
                                   to="Christoffer Viken <christoffer.viken@gmail.com>",
                                   subject="Uncaught enclosure!",
                                   body="Enclosures: %s \n\nConfig: %s" % (str(post['enc']), str(self.c['Fs']))
                                   )
                if self.c['owl']:
                    d = {"cfd":{"l":l, "t":t}, "call":"/tasks/pin/encr_rs.py"}
                else:
                    d = None
                return (post, d)
            except:
                logging.warning("Config problem on EncR cf")
                return (post, None)
        else:
            logging.warning("No config on EncR cf")
            return (post, None)
