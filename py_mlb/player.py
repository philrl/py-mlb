#!/usr/bin/env python
from fetcher import Fetcher
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
		self.logs = {}
		self.totals = {}
		self._categories = []
		self._attributes = []
		
		if self.player_id is not None:
			self.load()

	def getAttributes(self):
		"""
		Returns a list of player attribute names e.g. name_display_last_first
		"""
		return self._attributes

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

				self.totals[int(row['season'])] = log
			
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
		
		if self.primary_position == 1:
			f = Fetcher(Fetcher.MLB_PITCHER_URL, player_id=self.player_id, year=year)
		else:
			f = Fetcher(Fetcher.MLB_BATTER_URL, player_id=self.player_id, year=year)

		j = f.fetch()

		if self.primary_position == 1:
			parent = j['mlb_bio_pitching_last_10']['mlb_individual_pitching_game_log']['queryResults']
		else:
			parent = j['mlb_bio_hitting_last_10']['mlb_individual_hitting_game_log']['queryResults']

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
					val = row[key]
					key = key.upper()
					if val.isdigit():
						log[key] = int(val)
					else:
						try:
							log[key] = float(val)
						except ValueError:
							log[key] = str(val)
			
				if year not in self.logs:
					self.logs[year] = []

				self.logs[year].append(log)

	def load(self, id = None):
		"""
		Calls MLB.com server and loads player information
		
		Arguments:
		id : The MLB.com player ID
		"""
		if id is None and self.player_id is not None:
			id = self.player_id
		else:
			raise Exception('No player_id specified')

		f = Fetcher(Fetcher.MLB_PLAYER_URL, player_id=self.player_id)
		j = f.fetch()
		
		records = j['player_info']['queryResults']['row']
		for key, value in records.iteritems():
			setattr(self, key, value)
			self._attributes.append(key)

		self.loadYearlies()
		#self.loadGamelogs()
