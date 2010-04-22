#!/usr/bin/env python
from fetcher import Fetcher
from db import DB
import json
import datetime, time
import calendar
import re
from . import parseJSON

class Transactions(list):
	"""Transactions is a list of dict objects containing MLB transactions"""
	def __init__(self, year, month, day = None):
		"""
		Constructor
		
		Arguments:
		year: The... year!
		month: The... month!
		day: The... day! (or None for all days of the month)
		"""
		days = []
		
		if day is None:
			for d in xrange(1, calendar.mdays[month] + 1):
				days.append(datetime.date(year, month, d))
		else:
			days.append(datetime.date(year, month, day))

		begin = days[0]
		end = days[-1]

		f = Fetcher(Fetcher.MLB_TRANSACTION_URL, start=begin.strftime("%Y%m%d"), end=end.strftime("%Y%m%d"))
		try:
		 	obj = f.fetch()
			if obj['transaction_all']['queryResults']['totalSize'] == 0: return
			results = obj['transaction_all']['queryResults']['row']
			
			if type(results) is dict:
				self.append(results)
			else:
				for row in results:
					self.append(row)
		except (ValueError, KeyError), e:
			logger.error("ERROR %s on %s" % (e, f.url))
			pass


	def save(self):
		try:
			db = DB()
		except:
			return False

		for tr in self:
			db.savedict(tr, 'transaction')