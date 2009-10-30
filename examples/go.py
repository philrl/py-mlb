#!/usr/bin/env python
import logging
from py_mlb import player, team, league

"""uncomment to see HTTP logging
log = logging.getLogger('py_mlb.fetcher')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
"""

# Load and print player information and career totals for Ichiro! Suzuki
p = player.Player(400085)
for attr in p.getAttributes():
	print "%s: %s" % (attr, getattr(p, attr))

# Load and print the entire roster of the Seattle Mariners
l = league.League()
team = l.teams['sea']
team.fetchRoster()

for player_id, player in team.roster.iteritems():
	print player.name_full