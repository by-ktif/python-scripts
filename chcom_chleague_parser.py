# -*- coding: utf-8 -*-
"""parser of champinat.com schedules"""

__author__ = "Alexey Elisawetski"
__date__ = "$Date: 2013/11/02 08:19:00 $"

from BeautifulSoup import BeautifulSoup
import urllib
import re
import hashlib
import MySQLdb

con = MySQLdb.connect('localhost', 'root', '', 'ttlz')
con.set_character_set('utf8')
con.autocommit(True)
url = "http://www.championat.com/football/_ucl/765/calendar/tour/group.html"
#url = "http://www.championat.com/football/_spain/777/calendar/tour.html"
leagueId = 1


class Game:
	opponentA = -1
	opponentB = -1
	scoreA = -1
	scoreB = -1
	date = ""


def convertDate(stringDate):
	arrayDate = stringDate.split(' ');
	sf = "09"
	if arrayDate[1].encode('cp1251') == u'€нвар€'.encode('cp1251'):
		sf = "01"
	if arrayDate[1].encode('cp1251') == u'феврал€'.encode('cp1251'):
		sf = "02"
	if arrayDate[1].encode('cp1251') == u'марта'.encode('cp1251'):
		sf = "03"
	if arrayDate[1].encode('cp1251') == u'апрел€'.encode('cp1251'):
		sf = "04"
	if arrayDate[1].encode('cp1251') == u'ма€'.encode('cp1251'):
		sf = "05"
	if arrayDate[1].encode('cp1251') == u'июн€'.encode('cp1251'):
		sf = "06"
	if arrayDate[1].encode('cp1251') == u'июл€'.encode('cp1251'):
		sf = "07"
	if arrayDate[1].encode('cp1251') == u'августа'.encode('cp1251'):
		sf = "08"
	if arrayDate[1].encode('cp1251') == u'окт€бр€'.encode('cp1251'):
		sf = "10"
	if arrayDate[1].encode('cp1251') == u'но€бр€'.encode('cp1251'):
		sf = "11"
	if arrayDate[1].encode('cp1251') == u'декабр€'.encode('cp1251'):
		sf = "12"
	if len(arrayDate[0]) == 1:
		arrayDate[0] = '0'+ arrayDate[0]
	return "%s-%s-%s" % (arrayDate[2], sf, arrayDate[0])


def getHash(str):
	m = hashlib.md5()
	m.update(str)
	return m.hexdigest()


opponentDict = {}
curr = con.cursor()
curr.execute("SELECT id, name FROM ttlz.z_teams;")
data = curr.fetchall()
for row in data:
	opponentDict[getHash(row[1]).encode('utf8')]=row[0]

def getOpponenId(opponentName):
	opponentName = opponentName.encode('utf8')
	hash = getHash(opponentName)
	if hash in opponentDict:
		return opponentDict[hash]
	else:
		curr.execute('INSERT INTO ttlz.z_teams SET name=%s', (opponentName))
		curr.execute('SELECT id FROM ttlz.z_teams WHERE name=%s', (opponentName))
		newId = curr.fetchone()[0]
		opponentDict[hash] = newId
		return newId

page = urllib.urlopen(url)
soup = BeautifulSoup(page.read())
page.close()

linesTR = soup.findAll("tr", { "class" : re.compile(r"^tr_.$") })

date = ""
list = []
for line in linesTR:
	tds = line.findAll("td")
	if len(tds) > 1:
		ahrefs = tds[2].findAll("a")
		scoreString = tds[3].a.b.string
		game = Game()
		game.opponentA = getOpponenId(ahrefs[0].string)
		game.opponentB = getOpponenId(ahrefs[1].string)
		game.date = "%s %s:00" % (date, tds[1].string.strip())
		if scoreString:
			scores = scoreString.split(':');
			game.scoreA = scores[0]
			game.scoreB = scores[1]
		list.append(game)
	else:
		date = convertDate(tds[0].string)

for game in list:
	curr.execute('SELECT id, scoreA FROM ttlz.z_games WHERE starttime=%s AND teamA_id=%s', (game.date, game.opponentA))
	row = curr.fetchone()
	if row:
		if row[1] == -1 and game.scoreA > -1:
			curr.execute('UPDATE ttlz.z_games SET scoreA=%s, scoreB=%s WHERE id=%s', (game.scoreA, game.scoreB, row[0]))
	else:
		curr.execute('INSERT INTO ttlz.z_games SET league_id=%s, starttime=%s, teamA_id=%s, teamB_id=%s, scoreA=%s, scoreB=%s', (leagueId, game.date, game.opponentA, game.opponentB, game.scoreA, game.scoreB))
		
#	print "%s: %s - %s (%s:%s)" % (game.date, game.opponentA, game.opponentB, game.scoreA, game.scoreB)

curr.close()
con.close()
