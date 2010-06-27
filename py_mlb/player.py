#!/usr/bin/env python
from fetcher import Fetcher
from py_mlb import logger
from db import DB

import logging
import datetime

class Player(dict):
	"""A MLB player"""
	def __init__(self, player_id = None):
		"""
		Constructor
		
		Arguments:
		player_id : The MLB.com ID attribute for the given player
		"""
		self.player_id = player_id
		# game logs
		self.logs = {}
		# yearly totals
		self.totals = {}
		# career totals
		self.career = {}
		
		if self.player_id is not None: self.load()


	def loadYearlies(self):
		"""
		Loads yearly and career totals for a player
		"""
		if self['primary_position'] == 1:
			f = Fetcher(Fetcher.MLB_PITCHER_SUMMARY_URL, player_id=self.player_id)
		else:
			f = Fetcher(Fetcher.MLB_BATTER_SUMMARY_URL, player_id=self.player_id)
		
		j = f.fetch()
		
		# if the JSON object is empty, bail
		if len(j.keys()) == 0: return
		
		# get yearly totals
		if self['primary_position'] == 1:
			parent = j['mlb_bio_pitching_summary']['mlb_individual_pitching_season']['queryResults']
		else:
			parent = j['mlb_bio_hitting_summary']['mlb_individual_hitting_season']['queryResults']
		
		if parent['totalSize'] > 0:
			records = parent['row']

			# accounting for player with only one row
			if type(records) is dict: records = [records]
			
			for row in records:
				log = {}
				for key, value in row.iteritems(): log[key] = value
				self.totals[row['season']] = log
			
		# get career totals
		if self['primary_position'] == 1:
			parent = j['mlb_bio_pitching_summary']['mlb_individual_pitching_career']['queryResults']
		else:
			parent = j['mlb_bio_hitting_summary']['mlb_individual_hitting_career']['queryResults']
			
		if parent['totalSize'] > 0:
			for key, value in parent['row'].iteritems(): self.career[key] = value


	def loadGamelogs(self, year = None):
		"""
		Loads gamelogs for the player for a given year
		
		Arguments:
		year : The season desired. Defaults to the current year if not specified
		"""
		if year is None: year = datetime.datetime.now().year
		if year not in self.logs: self.logs[year] = []
		
		if 'primary_position' not in self:
			logger.error("no primary position attribute for " % self)
			return False

		url = Fetcher.MLB_PITCHER_URL if self['primary_position'] == 1 else Fetcher.MLB_BATTER_URL
		
		f = Fetcher(url, player_id=self.player_id, year=year)
		j = f.fetch()

		try:
			if self['primary_position'] == 1:
				parent = j['mlb_bio_pitching_last_10']['mlb_individual_pitching_game_log']['queryResults']
			else:
				if 'mlb_individual_hitting_last_x_total' in j:
					parent = j['mlb_individual_hitting_last_x_total']['mlb_individual_hitting_game_log']['queryResults']
				else:
					parent = j['mlb_bio_hitting_last_10']['mlb_individual_hitting_game_log']['queryResults']
		except KeyError, e:
			logger.error('no key for gamelogs found in %s' % f.url)
			return False

		if parent['totalSize'] > 0:
			records = parent['row']

			# accounting for player with only one row
			if type(records) is dict: records = [records]

			for row in records:
				log = {}	
				for key, value in row.iteritems(): log[key] = value
				
				# some fixes
				if 'era' in log and (log['era'] == '-.--' or log['era'] == '*.**'): log['era'] = None
				
				self.logs[year].append(log)


	def saveGamelogs(self):
		"""
		Saves player game logs to database
		"""
		try:
			db = DB()
		except:
			return False

		# need to check for empty and set to None
		for year, logs in self.logs.iteritems():
			for log in logs:
				table = 'log_pitcher' if self['primary_position'] == 1 else 'log_batter'
				log['player_id'] = self['player_id']
				db.savedict(log, table)


	def save(self):
		"""
		Saves player information to database
		"""
		try:
			db = DB()
		except:
			return False

		db.savedict(self, 'player')


	def load(self, id = None):
		"""
		Calls MLB.com server and loads player information. If call fails, '_error' property is set.
	
		Arguments:
		id : The MLB.com player ID
		"""
		if id is None and self.player_id is not None:
			id = self.player_id
			self['player_id'] = self.player_id
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

		for key, value in records.iteritems(): self[key] = value
		self.loadYearlies()


if __name__ == '__main__':
	from pprint import pprint
	#log = logging.getLogger('py_mlb')
	#log.setLevel(logging.DEBUG)
	#log.addHandler(logging.StreamHandler())
	
	batter = Player(400085)
	pitcher = Player(433587)
	pitcher.loadYearlies()
	pitcher.loadGamelogs()
	pitcher.save()
	pitcher.saveGamelogs()
