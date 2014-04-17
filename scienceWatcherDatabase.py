# file: scienceWatcherDatabase.py
# Winthrop Gillis (wgillis)
# This file contains the code (middleware) for accessing the database
# information. It takes care of connections, SQL writes, and data 
# gathering

# Import Postgresql db code
import psycopg2, os
# Import library to help access db on the web server
import urllib.parse as urlparse

class Database:

	def __init__(self):

		# get connection and cursor for use from the whole class
		# self.connection = psycopg2.connect('dbname=sciencewatch\
		# 	user=wgillis')

		# code for after development
		urlparse.uses_netloc.append("postgres")
		url = urlparse.urlparse(os.environ["DATABASE_URL"])
		self.connection = psycopg2.connect(
			    database=url.path[1:],
			    user=url.username,
		    	password=url.password,
		    	host=url.hostname,
		    	port=url.port)
		self.cursor = self.connection.cursor()
		# comment


	def save(self):

		self.connection.commit()

	def execute(self, statement, args=None):
		''' If including vars, make sure it is
		a tuple. Arguments are not required.'''
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
		'''Returns a boolean return value to determine if a user was
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
		
		if data and data[2] == pwd:
			return data[0]
		else:
			return None

	def getUsername(self, uid):

		self.execute('select username from users where id=%s', (uid,))
		ID = self.getOne()
		return ID[0]

	def addArticle(self, args):
		''' Adds article given the right parameters'''

		try:

			self.execute('''insert into articles
			(userid, username, articleurl, posttime, comments, title, tag, commentnum) 
			values (%s, %s, %s, %s, %s, %s, %s, 0)''', args)

			self.save()
			
			return True

		except Exception as e:

			return False

	def getArticles(self):
		'''return a list of articles'''

		self.execute('select articleurl, comments, title, tag, commentnum from articles order by posttime desc')
		arts = self.getall()
		return arts

# Need to add incrementing component to articles table to accurately displays number of comments
	def addComment(self, args):
		'''Adds a comment to the database.'''

		# SQL code for adding comment
		try:
			self.execute('insert into comments (commenturl, comment, username, time) values (%s,%s,%s,%s)', args)
			self.execute('update articles set commentnum = commentnum + 1 where comments=%s', (args[0],))
			self.save()
			return True

		except Exception as e:
			return False

	def getComments(self, url):
		'''Returns a list of all the comments regarding an article'''

		self.execute('select comment, username from comments where commenturl=%s order by time desc', (url,))
		return self.getall()

	def addFavorite(self, uid, articleUrl):
		# Add SQL code for adding a link to the favorites table
		username = self.getUsername(uid)

		self.execute('select comments, title from articles where articleurl=%s', (articleUrl,))
		data = self.getOne()

		self.execute('insert into favorites values (%s,%s,%s,%s,%s)', (uid, username, articleUrl, data[0], data[1]))
		self.save()
		return True


	def removeFavorite(self, uid, articleUrl):
		# Add SQL for removing link from favorites table

		self.execute('delete from favorites where id=%s and articleurl=%s', (uid, articleUrl))
		self.save()
		return True

	def checkFavorites(self, uid, articleUrl):
		self.execute('select articleurl from favorites where id=%s', (uid,))

		data = self.getall()

		if (articleUrl,) in data:
			return True
		else:
			return False

	def getUserPage(self, uid):
		# Add SQL for getting all of the favorites of the user
		self.execute('select * from favorites where id=%s', (uid,))
		data = self.getall()
		return data

	def getArticlesWithTag(self, tag):
		# Get every article, process the tags to see if tag is present
		# and return a list of tuples where such is present
		arts = self.getArticles()
		data = [art for art in arts if tag in art[3]]
		return data



