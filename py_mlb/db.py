#!/usr/bin/env python
from warnings import simplefilter
import MySQLdb
import ConfigParser, os

class DB:
	"""Super dumb wrapper around a MySQLdb connection object"""
	def __init__(self):
		config = ConfigParser.ConfigParser()
		config.read(['.db.cfg', os.path.expanduser('~/.db.cfg')])

		simplefilter("error", MySQLdb.Warning)

		if config.has_section('db') \
		and config.has_option('db', 'db'):
			c = {}
			for key, value in config._sections['db'].iteritems():
				if not key.startswith('__'):
					c[key] = value

			try:
				self.db = MySQLdb.connect(**c)
			except MySQLdb.Error, e:
				raise

	@property
	def rowcount(self):
		"""
		Returns the number of rows affected/returned by the last query
		"""
		return self._count

	def execute(self, sql, values = None):
		"""
		Executes a query
		
		Arguments:
		sql - The query
		values - A list of values to be bound
		"""
		self._count = None

		cursor = self.db.cursor()

		try:
			cursor.execute(sql, values)
		except MySQLdb.Warning, e:
			pass
			
		self._count = cursor.rowcount
		cursor.close()
	
	def save(self):
		"""
		Commits all transactions and closes the connection
		"""
		self.db.commit()
		self.db.close()