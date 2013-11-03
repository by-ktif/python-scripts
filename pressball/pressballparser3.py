"""parser.py sample parser"""

__author__ = "Alexey Elisawetski"
__date__ = "$Date: 2013/01/11 12:19:00 $"

from bs4 import BeautifulSoup
import urllib.request


for i in range(1, 10):
    url = "http://www.pressball.by/news/?page=%d" % i
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read())

    divLenta = soup.find("div", { "id" : "lenta" })
    tables = divLenta.findAll('table', { "class" : "table mb10" })

    for table in tables:
        if table.parent['class'][0] == "lenta_top_news":
            continue
        links = table.findAll('a')
        for link in links:
            if link.parent.span:
                mlist = [x.strip() for x in link.parent.span.string.split('/')]
                (view, comments) = ("0", "0")
                if len(mlist)==2:
                    (view, comments) = mlist
                if len(mlist)==1:
                    view = mlist[0]
                if int(view) > 8000 or int(comments) > 100:
                    print("%s : %s" % (link.parent.span.string, link.get('href')))
