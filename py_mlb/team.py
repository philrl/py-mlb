#!/usr/bin/env python
from fetcher import Fetcher
from db import DB
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
		f = Fetcher(Fetcher.MLB_ROSTER_URL, team_id=self.team_id)
		j = f.fetch()
		
		if not j.has_key('roster_40'):
			return
		
		parent = j['roster_40']['queryResults']
		
		if int(parent['totalSize']) > 0:
			for record in parent['row']:
				player_id = record['player_id']
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
	
	def save(self):
		try:
			db = DB()
		except:
			return False
		
		sql = 'SELECT * FROM team WHERE team_id = %d' % self.team_id
		db.execute(sql)

		if db.rowcount == 0:
			a = {}
			for attr in self.__dict__.keys():
				if not attr == 'roster':
					a['`%s`' % attr] = getattr(self, attr)
			
			sql = 'INSERT INTO team (%s) VALUES (%s)' % (','.join(a.keys()), ','.join(['%s'] * len(a.keys())))
			db.execute(sql, a.values())
		
		db.save()