import urllib
from bs4 import BeautifulSoup#, SoupStrainer
from HTMLParser import HTMLParser

opener = urllib.FancyURLopener({})
path = '/home/ivan/temp/'


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

#grab html source from given url, and parse to get only text

def getHtml(url):
    resp = opener.open(url)
    return resp.read()

def getSoup(url):
    #returns unindented html source code (soup)
    return BeautifulSoup(getHtml(url))

def getSTxt(url):
    #gets text from soup from url
    soup = BeautifulSoup(getHtml(url))
    return soup.get_text()

def getPretty(url):
    #prettified soup
    soup = BeautifulSoup(getHtml(url))
    return soup.prettify()

def strToFile(text,fname):
    #create a file fpath with given text
    fpath = path + fname + '.txt'
    with open(fpath,'w') as f:
        f.write(repr(text))