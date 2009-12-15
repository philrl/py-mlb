#!/usr/bin/env python
import re
import json
import libxml2
import urllib2
import sys

from . import logger

class Fetcher:
	"""
	Responsible for all calls to MLB.com servers as well as parsing the responses
	"""

	# URL for the league
	MLB_LEAGUE_URL = "http://mlb.mlb.com/properties/mlb_properties.xml"
	# roster for a particular team
	MLB_ROSTER_URL = "http://mlb.mlb.com/lookup/json/named.roster_40.bam" \
		"?team_id=%team_id%"
	# player detail
	MLB_PLAYER_URL = "http://mlb.com/lookup/json/named.player_info.bam" \
		"?sport_code='mlb'&player_id='%player_id%'"
	# pitcher gamelogs
	MLB_PITCHER_URL = "http://mlb.com/lookup/json/named.mlb_bio_pitching_last_10.bam" \
		"?results=100&game_type='R'&season=%year%&player_id=%player_id%"
	# pitcher career and season totals
	MLB_PITCHER_SUMMARY_URL = "http://mlb.com/lookup/json/named.mlb_bio_pitching_summary.bam" \
		"?game_type='R'&sort_by='season_asc'&player_id=%player_id%"
	# batter gamelogs
	MLB_BATTER_URL = "http://mlb.com/lookup/json/named.mlb_bio_hitting_last_10.bam" \
		"?results=165&game_type='R'&season=%year%&player_id=%player_id%"
	# batter career and season totals
	MLB_BATTER_SUMMARY_URL = "http://mlb.mlb.com/lookup/json/named.mlb_bio_hitting_summary.bam" \
		"?game_type='R'&sort_by='season_asc'&player_id=%player_id%"
		
	# NOT YET USED
	MLB_SCHEDULE_URL = "http://mlb.mlb.com/components/schedule/schedule_%date%.json"
	MLB_STANDINGS_URL = "http://mlb.mlb.com/lookup/named.standings_all_league_repeater.bam?sit_code=%27h0%27&season=2005&league_id=103&league_id=104"
	
	def __init__(self, url, **kwargs):
		"""
		Constructor
		
		url : URL to fetch, one of the URLs defined in the Fetcher class
		kwargs : Any passed keyword is replaced into the URL with %key% format		
		"""
		for key in kwargs.keys():
			url = url.replace('%%%s%%' % key, str(kwargs[key]))
		
		url = re.sub('%%.+?%%', '', url)
		self.url = url

	def _parseJSON(self, obj):
		"""
		Recursively parses a JSON object to properly cast ints and floats
		
		Arguments:
		obj : The JSON object
		"""
		newobj = {}

		for key, value in obj.iteritems():
			key = str(key)

			if isinstance(value, dict):
				newobj[key] = self._parseJSON(value)
			elif isinstance(value, list):
				if key not in newobj:
					newobj[key] = []
					for i in value:
						newobj[key].append(self._parseJSON(i))
			elif isinstance(value, unicode):
				newobj[key] = self._formatValue(value)
			
		return newobj

	def _formatValue(self, val):
		"""
		Returns a properly casted variable for val
		"""
		if val.isdigit():
			val = int(val)
		else:
			try:
				val = float(val)
			except ValueError:
				val = val
		
		return val

	def fetch(self):
		"""
		Makes the HTTP request to the MLB.com server and handles the response
		"""
		req = urllib2.Request(self.url)
		
		if self.url.find('xml') >= 0:
			reqType = 'XML'
		elif self.url.find('json') >= 0:
			reqType = 'JSON'
		else:
			reqType = 'HTML'

		logger.debug("fetching %s" % self.url)

		try:
			res = urllib2.urlopen(req)
		except urllib2.URLError, e:
			logger.error("error fetching %s" % self.url)
			return []

		if reqType == 'JSON':
			# remove code comments that MLB puts in the response
			content = re.sub('\/\*.+?\*\/', '', res.read())
			
			try:
				obj = json.loads(content)
				return self._parseJSON(obj)
			except Exception, e:
				# log the error and return an empty object
				logger.error("error parsing %s\n%s\n%s" % (self.url, e, content))
				return {}
		elif reqType == 'XML':
			"""
			need to abstract this a lot more, currently XML is only for the team list
			and like as you see it returns specific nodes - it needs to just return an
			object and then that should be traversed elsewhere.
			"""
			obj = []
			xml = libxml2.parseDoc(res.read())
			ctxt = xml.xpathNewContext()
			nodes = ctxt.xpathEval("/mlb/leagues/league[@club='mlb']/teams/team")
			
			if len(nodes) != 30:
				return obj
				
			for node in nodes:
				team = {}
				for prop in node.properties:
					val = prop.content
					team[prop.name] = self._formatValue(prop.content)
				obj.append(team)
				
			xml.freeDoc()
			ctxt.xpathFreeContext()
			return obj
		elif reqType == 'HTML':
			return res.read()
