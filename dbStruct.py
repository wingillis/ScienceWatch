import psycopg2
import os
import urllib.parse as urlparse


class DbStruct:

	def __init__(self):

		# urlparse.uses_netloc.append("postgres")
		# url = urlparse.urlparse(os.environ["DATABASE_URL"])
		try:
			# self.connection = psycopg2.connect(
			#     database=url.path[1:],
			#     user=url.username,
		 #    	password=url.password,
		 #    	host=url.hostname,
		 #    	port=url.port)

			# If that doesn't work, on local database, use:
			self.connection = psycopg2.connect('dbname=sciencewatch user=wgillis')

			self.cursor = self.connection.cursor()

		except Exception as e:

			pass

	def close(self):

		self.connection.commit()
		self.cursor.close()
		self.connection.close()

	def save(self):

		self.connection.commit()

	def execute(self, statement, args=None):
		''' If including vars, make sure it is
		a tuple'''
		if args:
			self.cursor.execute(statement, args)
		else:
			self.cursor.execute(statement)

	def getOne(self):
		'''Returns a tuple of information'''
		return self.cursor.fetchone()

	def getall(self):
		'''Returns a list of tuples of information'''
		return self.cursor.fetchall()

	def addUser(self, uname, pwd):
		'''Gives a boolean return value to determine if a user was
		created or not'''
		try:
			self.execute('insert into users (username, password) values (%s, %s)', (uname, pwd))
			self.save()
			return True
		except Exception as e:
			return False

	def checkLogIn(self, user, pwd):
		'''Returns the user's id if they exist and give the right
		password, otherwise returns None'''
		self.execute('select * from users where username = %s', (user,))
		data = self.getOne()
		if data[2] == pwd:
			return data[0]
		else:
			return None

	def getUsername(self, uid):

		self.execute('select username from users where id=%s', (uid,))
		ID = self.getOne()
		return ID[0]


	def addArticle(self, args):
		try:
			self.execute('insert into articles (userid, username, articleurl, posttime, comments, title) values (%s, %s, %s, %s, %s, %s)', args)
			self.save()
			return True
		except Exception as e:

			return False

	def getFirst12Articles(self):
		'''return a list of first ten articles'''
		self.execute('select articleurl, comments, title from articles order by posttime desc limit 12')
		arts = self.getall()
		return arts



