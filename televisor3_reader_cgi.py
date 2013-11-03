#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
from BeautifulSoup import BeautifulSoup 
import urllib
import cgitb
cgitb.enable()

print "Content-Type: text/html"
print

print "<html><head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'><meta http-equiv='Content-Language' content='ru'></head><body>"

for i in range (690, 695):
    url = "http://www.sports.ru/tribuna/blogs/televizor3/?p=%d" % i
    page = urllib.urlopen(url)
    soup = BeautifulSoup(page.read())
    anonsy = soup.findAll('div', { "class" : "anons" })
    for anons in anonsy:
        plus = anons.find("span", {"class" : "text-plus"})
        if int(plus.string) >= 50  :
            print(anons)
            postId = anons.get("data-materialid")
            commentsPage = urllib.urlopen("http://www.sports.ru/api/comment/get/message.html?message_class=Sports::Blog::Post::Post&layout=1&order_type=top10&message_id=%s" % postId)
            soupComments =  BeautifulSoup(commentsPage.read())
            comments = soupComments.findAll('div', {"class" : "comment-text"})
            for comment in comments:
                rate = comment.find("span", {"class" : "rate-text text-plus"})
                if int(rate.string) >= 10:
                    print(comment)
            commentsPage.close()
    
    print "</body></html>"
    page.close()
