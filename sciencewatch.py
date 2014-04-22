# file: sciencewatch.py 
# Winthrop Gillis (wgillis)
# 4/9/2014
# This is the main file for the ScienceWatchr app
# it contains all the handling for webpages, redirection, etc

# Web framework import
from flask import Flask, redirect, request, session, flash, render_template, make_response
# Necessary libraries import
import time, math
# Import secret key to make user session secure
import secretKey
# Import the database middleware built for website
import scienceWatcherDatabase
# import ultility functions used by the web app
import utilities

# create the application
app = Flask(__name__)
# add the secret key so users can log in with an account
app.secret_key = secretKey.key

# create the database object
db = scienceWatcherDatabase.Database()


#################################################################################

# app.route() calls whatever function directly below it because it's a decorator
# when that specific url relative to the homepage address is

# Redirect user to the real homepage, which is page one of all the articles
@app.route('/')
def home():
	return redirect('/page/1')


#################################################################################

# Real home page, displays all the articles and can sign the user in
@app.route('/page/<number>', methods=['GET','POST'])
def index(number=0):
	# If the form request is a post method and not a get, sign the user in
	if request.method == 'POST':
		if 'pwd' in request.form:
			user = signIn(request)
			if number:
				return redirect('/page/%s' % number)
			else:
				return redirect('/page/1')
		elif 'fav' in request.form:
			user = session['uuid']
			artURL = request.form['fav']
			isFav = db.checkFavorites(user, artURL)
			if isFav:
				db.removeFavorite(user, artURL)
				return make_response('No')
			else:
				db.addFavorite(user, artURL)
				return make_response('Yes')

		return make_response('It didn\'t work')

	# this is for every other time the user accesses this page
	else:
		# get all the articles
		content = db.getArticles()
		# find how many articles there are for the paginator
		totalContent = len(content)
		# depending on how many articles there are, there will be
		# a maximum amount of pages of articles
		maxPages = math.ceil(totalContent/12)
		# this is the page number
		# we can go through all the articles in multiples of 12 to display them
		# on each page
		if number:
			num = int(number)
			accessContent = (num-1) * 12
		else:
			accessContent = 0
		# only get the 12 relevant articles for display, or whatever is left
		# if there are less than 12 articles to display
		content = content[accessContent:accessContent+12]
		# prepare the data structure for holding the data being passed into the html
		k = len(content)

		if k < 4:
			rows = [[] for i in range(k)]
		else:
			rows = [[] for i in range(4)]
		
		uuid = ''
		uname = ''
		if 'uuid' in session:
			uuid = session['uuid']
			uname = db.getUsername(uuid)

			data = [utilities.Article(article + (index%5, db.checkFavorites(uuid, article[0]))) for index, article in enumerate(content)]
		else:
			data = [utilities.Article(article + (index%5, False)) for index, article in enumerate(content)]

		# create the data structure to be passed to the html
		for index, datum in enumerate(data):
			rows[index%4].append(datum)

		# set up username variable to display the user's name 
		

		return render_template('articles.html', uname = uname, rows=rows, page=num, totalPages=maxPages, uuid = uuid)

#################################################################################

# whenever the user wants to log out, they are directed to this address
@app.route('/logout')
def logout():
	session.pop('uuid', None)
	session.pop('logged_in', None)
	return redirect('/')

#################################################################################

# show the registration page so users can make a profile
@app.route('/register', methods=['GET', 'POST'])
def register():
	# try to add the new user
	if request.method == 'POST':
		user = request.form['user']
		pwd = request.form['pwd']
		status = db.addUser(user, pwd)
		if status:
			uuid = db.getID(user)
			session['uuid'] = uuid
			session['logged_in'] = True
			return redirect('/page/1')
		else:
			flash('Username probably taken, try another')
			return render_template('register.html')
	else:
		# render login form
		return render_template('register.html')

#################################################################################

# form for posting an article
@app.route('/postArticle', methods=['GET','POST'])
def postArticle():
	if request.method == 'POST':
		if 'user' in request.form:
			user = signIn(request)
			return redirect('/postArticle')
		elif 'artUrl' in request.form:
			c = utilities.generateURL()
			u = db.getUsername(session['uuid'])
			args = (session['uuid'], u, request.form['artUrl'], time.time(), c,
				request.form['title'], request.form['tag'])
			state = db.addArticle(args)
			# do this if everything worked as expected
			if state:
				return redirect('/page/1')
			else:
				return '404'
	else:
		u = ''
		if 'uuid' in session:
			u = db.getUsername(session['uuid'])
		return render_template('postArticle.html', uname=u)

#################################################################################

# This page displays any comments associated with an article
@app.route('/<commenturl>', methods=['GET','POST'])
def comment(commenturl):
	if request.method == 'POST':

		if 'user' in request.form:

			user = signIn(request)
			return redirect('/%s' % (commenturl))

		elif 'comment' in request.form:

			u = db.getUsername(session['uuid'])

			com = request.form['comment']

			db.addComment((commenturl, com, u, time.time()))

			return redirect('/{0}'.format(commenturl))
	else:

		db.execute('select articleurl, comments, title from articles where comments=%s', (commenturl,))
		data = db.getOne()
		if data:
			title = data[2]
			articleurl = data[0]
			name = ''
			comms = db.getComments(commenturl)
			struct = [utilities.Comment((com[1],com[0], index)) for index, com in enumerate(comms)]
			if 'uuid' in session:
				name = db.getUsername(session['uuid'])
			return render_template('comments.html', title=title, url=articleurl, comments=struct, uname=name)
		else:
			return 'Does not exist'


#################################################################################

# show the user's profile and all the posts and comments s/he made
# OR show all the favorites that the user has saved
@app.route('/profiles/<uid>', methods = ['GET', 'POST'])
def profile(uid=None):
	if request.method == 'POST':

		if 'user' in request.form:

			user = signIn(request)
			return redirect('/profiles/%s' % (uid))

	else:	
		if uid:
			try:
				uuid = ''
				uname = ''
				if 'uuid' in session:
					uuid = session['uuid']
					uname = db.getUsername(uuid)
				int(uid)
				favorites = db.getUserPage(uid)
				data = [utilities.Favorite(fav + (index%5,)) for index, fav in enumerate(favorites)]
				return render_template('favorites.html', uname = uname, uuid = uuid, favorites = data, profile = db.getUsername(uid))
			except:
				return 'Please use person\'s id that exists'
			

		else:
			return 'Page doesn\'t exist'

#################################################################################

@app.route('/tag/<tag>', methods=['GET', 'POST'])
def tagPage(tag=None):
	if request.method == 'POST':	
		user = signIn(request)
		return redirect('/tag/{0}'.format(tag))
	if tag:
		content = db.getArticlesWithTag(tag)

		
		# only get the 12 relevant articles for display, or whatever is left
		# if there are less than 12 articles to display
		# prepare the data structure for holding the data being passed into the html
		k = len(content)

		if k < 4:
			rows = [[] for i in range(k)]
		else:
			rows = [[] for i in range(4)]
		# k will at max be 12
		
		uuid = ''
		uname = ''
		if 'uuid' in session:
			uuid = session['uuid']
			uname = db.getUsername(uuid)

			data = [utilities.Article(article + (index%5, db.checkFavorites(uuid, article[0]))) for index, article in enumerate(content)]
		else:
			data = [utilities.Article(article + (index%5, False)) for index, article in enumerate(content)]
		# create the data structure to be passed to the html
		# for index, row in enumerate(rows):
		# 	articles = data[index * int(k/3): (index * int(k/3)) + math.ceil(k/3)]
		# 	for article in articles:
		# 		rows[index].append(article)

		for index, datum in enumerate(data):
			rows[index%4].append(datum)

		

		return render_template('articles.html', uname = uname, rows = rows, page = 1, totalPages = 1, uuid = uuid)



#################################################################################
def signIn(r):
	# Get the user from the signin form
	user = r.form['user']
	pwd = r.form['pwd']
	login = db.checkLogIn(user, pwd)
	if login:
		session['uuid'] = login
		session['logged_in'] = True
		return user
	else:
		# Username is not in database, so do something about it
		# Form a response
		flash('Username or password not correct')
		return ''



#################################################################################
if __name__ == '__main__':
	app.run(debug=True)
