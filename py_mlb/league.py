#!/usr/bin/env python
from fetcher import Fetcher
import team

class League:
	"""Represents the league"""
	def __init__(self):
		self.teams = {}
		self.load()

	def load(self):
		"""
		Calls MLB.com server and loads all team information
		"""
		f = Fetcher(Fetcher.MLB_LEAGUE_URL)

		for item in f.fetch():
			t = team.Team(item)
			self.teams[t.team_code] = t