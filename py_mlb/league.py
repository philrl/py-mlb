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
			self.teams[t['team_code']] = t


	def save(self):
		for team_code, team in self.teams.iteritems(): team.save()


if __name__ == '__main__':
	import logging
	log = logging.getLogger('py_mlb')
	log.setLevel(logging.DEBUG)
	log.addHandler(logging.StreamHandler())

	league = League(True)
	league.save()