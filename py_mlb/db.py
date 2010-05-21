#!/usr/bin/env python
from warnings import simplefilter
import MySQLdb
import ConfigParser, os

from py_mlb import logger

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


	def savedict(self, obj, table):
		"""
		Persists a dict to a specified table, assumes all keys in dict are
		valid columns in table
		"""
		if not isinstance(obj, dict): return False

		keys = ['`%s`' % key for key in obj.keys()]
		values = [None if value == '' else value for value in obj.values()]

		sql = 'REPLACE INTO %s (%s) VALUES (%s)' % (table, ','.join(keys), ','.join(['%s'] * len(values)))
		self.execute(sql, values)


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
			self.db.commit()
		except (MySQLdb.Warning, MySQLdb.Error), e:
			logger.error('QUERY ERROR: %s\nQUERY: %s\nVALUES: %s\n\n' % (e, sql, ','.join([str(v) for v in values])))
			pass

		self._count = cursor.rowcount
		cursor.close()


	def close(self):
		"""
		Closes the database connection
		"""
		self.db.close()