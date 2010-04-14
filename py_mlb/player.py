#!/usr/bin/env python
from fetcher import Fetcher
from . import logger
from db import DB

import datetime

class Player:
	"""A MLB player"""
	def __init__(self, player_id = None):
		"""
		Constructor
		
		Arguments:
		player_id : The MLB.com ID attribute for the given player
		"""
		self.player_id = player_id
		self._logs = {}
		self._totals = {}
		self._categories = []
		
		if self.player_id is not None:
			self.load()

	def getAttributes(self):
		"""
		Returns a list of player attribute names e.g. name_display_last_first
		"""
		return [attr for attr in self.__dict__.keys() if not attr.startswith('_')]

	def getCategories(self):
		"""
		Returns a list of statistical categories
		"""
		return self._categories
	
	def loadYearlies(self):
		"""
		Loads yearly and career totals for a player
		"""
		if self.primary_position == 1:
			f = Fetcher(Fetcher.MLB_PITCHER_SUMMARY_URL, player_id=self.player_id)
		else:
			f = Fetcher(Fetcher.MLB_BATTER_SUMMARY_URL, player_id=self.player_id)
		
		j = f.fetch()
		
		# if the JSON object is empty, bail
		if len(j.keys()) == 0:
			return
		
		# get yearly totals
		if self.primary_position == 1:
			parent = j['mlb_bio_pitching_summary']['mlb_individual_pitching_season']['queryResults']
		else:
			parent = j['mlb_bio_hitting_summary']['mlb_individual_hitting_season']['queryResults']
		
		if int(parent['totalSize']) > 0:
			records = parent['row']

			# accounting for player with only one row
			if isinstance(records, dict):
				row = records
				records = []
				records.append(row)
			
			for row in records:
				log = {}
				for key, value in row.iteritems():
					log[key] = value

				self._totals[int(row['season'])] = log
			
		# get career totals and set them as instance attributes
		if self.primary_position == 1:
			parent = j['mlb_bio_pitching_summary']['mlb_individual_pitching_career']['queryResults']
		else:
			parent = j['mlb_bio_hitting_summary']['mlb_individual_hitting_career']['queryResults']
			
		if int(parent['totalSize']) > 0:
			records = parent['row']
			for key, value in records.iteritems():
				setattr(self, key, value)
				self._categories.append(key)
			
	def loadGamelogs(self, year = None):
		"""
		Loads gamelogs for the player for a given year
		
		Arguments:
		year : The season desired. Defaults to the current year if not specified
		"""
		if year is None:
			year = datetime.datetime.now().year
		
		if 'primary_position' not in self.__dict__:
			logger.error("no primary position attribute for " % self.__dict__)
			return False
		
		if self.primary_position == 1:
			f = Fetcher(Fetcher.MLB_PITCHER_URL, player_id=self.player_id, year=year)
		else:
			f = Fetcher(Fetcher.MLB_BATTER_URL, player_id=self.player_id, year=year)

		j = f.fetch()

		try:
			if self.primary_position == 1:
				parent = j['mlb_bio_pitching_last_10']['mlb_individual_pitching_game_log']['queryResults']
			else:
				parent = j['mlb_bio_hitting_last_10']['mlb_individual_hitting_game_log']['queryResults']
		except KeyError, e:
			logger.error('no key for gamelogs found in %s' % f.url)
			return False

		if int(parent['totalSize']) > 0:
			records = parent['row']

			# accounting for player with only one row
			if isinstance(records, dict):
				row = records
				records = []
				records.append(row)
		
			for row in records:
				log = {}
			
				for key in row.keys():
					key = str(key)
					val = str(row[key])
					key = key.upper()
					if val.isdigit():
						log[key] = int(val)
					else:
						try:
							log[key] = float(val)
						except ValueError:
							log[key] = str(val)
			
				if year not in self._logs:
					self._logs[year] = []

				self._logs[year].append(log)

	def saveGamelogs(self):
		"""
		Saves player game logs to database
		"""
		try:
			db = DB()
		except:
			return False

		for year in self._logs.keys():
			for log in self._logs[year]:
				table = 'log_pitcher' if self.primary_position == 1 else 'log_batter'
				sql = 'SELECT * FROM %s WHERE GAME_ID = \'%s\' AND PLAYER_ID = \'%s\'' % (table, log['GAME_ID'], self.player_id)
				db.execute(sql)

				if db.rowcount == 0:
					log['PLAYER_ID'] = self.player_id

					sql = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(log.keys()), ','.join(['%s'] * len(log.keys())))
					db.execute(sql, log.values())

		db.save()
				
	def save(self):
		"""
		Saves player information to database
		"""
		try:
			db = DB()
		except:
			return False
		
		a = {}
		for attr in [attr for attr in self.__dict__.keys() if not attr.startswith('_')]:
			if attr.endswith('_date') and getattr(self, attr) == '' \
			or attr == 'jersey_number' and getattr(self, attr) == '':
				value = None
			else:
				value = getattr(self, attr)
		
			a[attr] = value
			
		sql = 'REPLACE INTO player (%s) VALUES (%s)' % (','.join(a.keys()), ','.join(['%s'] * len(a.values())))
		db.execute(sql, a.values())
		db.save()

	def load(self, id = None):
		"""
		Calls MLB.com server and loads player information. If call fails, '_error' property is set.
	
		Arguments:
		id : The MLB.com player ID
		"""
		if id is None and self.player_id is not None:
			id = self.player_id
		else:
			raise Exception('No player_id specified')

		f = Fetcher(Fetcher.MLB_PLAYER_URL, player_id=self.player_id)
		j = f.fetch()
		
		try:
			records = j['player_info']['queryResults']['totalSize']
		except KeyError, e:
			msg = 'ERROR on %s: totalSize not returned for call' % f.url
			self._error = msg
			logger.error(msg)
			return False

		if records == 0:
			msg = 'ERROR on %s: totalSize is 0' % f.url
			self._error = msg
			logger.error(msg)
			return False

		try:
			records = j['player_info']['queryResults']['row']
		except KeyError, e:
			self._error = 'ERROR on %s: key %s not found' % (f.url, e)
			logger.error('ERROR on %s: key %s not found\n%s' % (f.url, e, j))
			return False

		for key, value in records.iteritems():
			setattr(self, key, value)

		self.loadYearlies()
