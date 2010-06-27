#!/usr/bin/env python
import re
import json
import libxml2
import urllib2
import sys

from py_mlb import logger, parseJSON, formatValue

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
	# scheduling
	MLB_SCHEDULE_URL = "http://mlb.mlb.com/components/schedule/schedule_%date%.json"
	# transactions
	MLB_TRANSACTION_URL = "http://web.minorleaguebaseball.com/lookup/json/named.transaction_all.bam" \
		"?league_id=104&start_date=%start%&end_date=%end%"
	# transactions archive - not yet used
	MLB_TRANSACTION_URL_ARCHIVE = "http://web.minorleaguebaseball.com/gen/stats/jsdata/2005/leagues/l113_200507_tra.js"
		
	# NOT YET USED
	MLB_STANDINGS_URL = "http://mlb.mlb.com/lookup/named.standings_all_league_repeater.bam" \
		"?sit_code=%27h0%27&season=2005&league_id=103&league_id=104"
	
	def __init__(self, url, **kwargs):
		"""
		Constructor
		
		url : URL to fetch, one of the URLs defined in the Fetcher class
		kwargs : Any passed keyword is replaced into the URL with %key% format		
		"""
		for key in kwargs.keys():
			url = url.replace('%%%s%%' % key, str(kwargs[key]))
		
		# get rid of any unmatched %key% fields
		url = re.sub('%%.+?%%', '', url)
		self.url = url

	def fetch(self, returnRaw = False):
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
			content = res.read()
		except (urllib2.URLError, IOError), e:
			return {}

		if returnRaw:
			return content

		if reqType == 'JSON':
			# remove code comments that MLB puts in the response
			content = re.sub('\/\*.+?\*\/', '', content)
			
			try:
				obj = json.loads(content)
				return parseJSON(obj)
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
			xml = libxml2.parseDoc(content)
			ctxt = xml.xpathNewContext()
			nodes = ctxt.xpathEval("/mlb/leagues/league[@club='mlb']/teams/team")
			
			if len(nodes) != 30:
				return obj
				
			for node in nodes:
				team = {}
				for prop in node.properties:
					val = prop.content
					team[prop.name] = formatValue(prop.content)
				obj.append(team)
				
			xml.freeDoc()
			ctxt.xpathFreeContext()
			return obj
		elif reqType == 'HTML':
			return content
