#!/usr/bin/env python
from fetcher import Fetcher
import team

class League:
	"""Represents the league"""
	def __init__(self, loadRosters = False):
		"""
		Constructor

		Arguments:
		loadRosters : If true, rosters will automatically be loaded (more HTTP requests!)
		"""
		self.teams = {}
		self.load(loadRosters)

	def load(self, loadRosters = False):
		"""
		Calls MLB.com server and loads all team information

		Arguments:
		loadRosters : If true, rosters will automatically be loaded (more HTTP requests!)
		"""
		f = Fetcher(Fetcher.MLB_LEAGUE_URL)

		for item in f.fetch():
			t = team.Team(item)
			if loadRosters:
				t.loadRoster()
			self.teams[t.team_code] = t