#!/usr/bin/env python
from fetcher import Fetcher
from db import DB
import json
import datetime, time
import calendar
import re
from . import parseJSON

class Schedule(dict):
	"""The schedule for a given day"""
	def __init__(self, year, month, day = None):
		"""
		Constructor
		
		Arguments:
		year: The... year!
		month: The... month!
		day: The... day! (or None for all days of the month)
		
		Schedule is a standard dictionary: each day is a key in the format of 'YYYY-MM-DD', each value
		a list of game dictionaries.
		"""
		days = []
		
		if day is None:
			for d in xrange(1, calendar.mdays[month] + 1):
				days.append(datetime.date(year, month, d))
		else:
			days.append(datetime.date(year, month, day))

		for d in days:
			key = d.strftime("%Y-%m-%d")
			if key not in self.keys():
				self[key] = []

			f = Fetcher(Fetcher.MLB_SCHEDULE_URL, date=d.strftime("%Y%m%d"))
			try:
			 	content = f.fetch(True)
				if len(content) == 0: continue
				content = re.sub(r'\t+', '\t', content)
				content = content.replace('"', '\\"')
				content = content.replace("'", "\"")
				content = re.sub(r'\t([\w,_]+):\s', r'"\1":', content)
				obj = json.loads(content)
				self[key] = obj
			except ValueError, e:
				print "ERROR %s on %s" % (e, f.url)
				pass
	
	def save(self):
		try:
			db = DB()
		except:
			return False

		for day, games in self.iteritems():
			for game in games:
				
				game['home_team_id'] = game['home']['id']
				game['home_team_full'] = game['home']['full']
				game['home_team_display_code'] = game['home']['display_code']
				game['home_probable_id'] = game['home']['probable_id']
				game['away_team_id'] = game['away']['id']
				game['away_team_full'] = game['away']['full']
				game['away_team_display_code'] = game['away']['display_code']
				game['away_probable_id'] = game['away']['probable_id']
				game['game_date'] = game['game_id'][0:10].replace('/', '-')
				
				if game['game_status'] == 'F':
					game['home_score'] = game['home']['result']
					game['away_score'] = game['away']['result']
				else:
					game['home_score'] = None
					game['away_score'] = None

				del(game['home'])
				del(game['away'])
				del(game['pitcher'])
				
				sql = 'REPLACE INTO schedule (%s) VALUES (%s)' % (','.join(game.keys()), ','.join(['%s'] * len(game.values())))
				db.execute(sql, game.values())
			
		db.close()
