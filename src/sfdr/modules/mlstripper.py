"""
Created on 24. mars 2011

@author: "Christoffer Viken"
"""
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    """
    Strips HTML out of the feed
    TODO: More lightweight HTML stripper needed
    """
    s = MLStripper()
    s.feed(html)
    return s.get_data()
