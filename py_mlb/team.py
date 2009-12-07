#!/usr/bin/env python
from fetcher import Fetcher
from BeautifulSoup import BeautifulSoup
import re
import player

class Team:
	"""Represents a team"""
	def __init__(self, attributes):
		"""
		Constructor
		
		Arguments:
		attributes - A dict of key/value pairs used to populate the team, passed by the league information
		"""
		self.roster = {}
		for key, value in attributes.iteritems():
			setattr(self, key, value)
	
	def loadRoster(self):
		"""
		Calls MLB.com servers to obtain the complete roster for the team. UNFORTUNATELY it's using HTML parsing
		"""
		f = Fetcher(Fetcher.MLB_ROSTER_URL, team_code=self.team_code)
		html = f.fetch()
		
		soup = BeautifulSoup(f.fetch())
		rows = soup.findAll('a')
		
		for row in rows:
			row = str(row)
			matches = re.search(r'player_id\=(\d+?)"', row)
			if matches:
				player_id = int(matches.group(1))
				self.roster[player_id] = player.Player(player_id)
		
	def getPlayer(self, player_id):
		"""
		Returns a player object, or None
		
		Arguments:
		player_id - The MLB.com player ID
		"""
		if player_id in self.roster.keys():
			return self.roster[player_id]
		else:
			return None