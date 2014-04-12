# file: sciencewatch.py 
# Winthrop Gillis (wgillis)
# 4/9/2014
# This is the main file for the ScienceWatchr app
# it contains all the handling for webpages, redirection, etc

# Web framework import
from flask import Flask, redirect, request, session, flash, render_template
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
		user = signIn(request)
		if number:
			return redirect('/page/%s' % number)
		else:
			return redirect('/page/1')

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
		rows = [[] for i in range(4)]
		# k will at max be 12
		k = len(content)

		# for the html layout, I need to double-up all the content data, so this
		# will give me up to six entries in the list
		data = [utilities.Article(content[i]+ (i%5,)) for i in range(0,k)]

		# k will now be at max 6
		k = len(data)

		# create the data structure to be passed to the html
		for index, row in enumerate(rows):
			articles = data[index * 3: (index * 3) + 3]
			for article in articles:
				rows[index].append(article)

		# set up username variable to display the user's name 
		uname = ''
		if 'uuid' in session:
			uname = db.getUsername(session['uuid'])

		return render_template('articles.html', uname = uname, rows=rows, page=num, totalPages=maxPages)

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
			db.execute('select (id) from users where username=%s', (user,))	
			uuid = db.getOne()[0]
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
			struct = [utilities.Comment((com[1],com[0])) for com in comms]
			if 'uuid' in session:
				name = db.getUsername(session['uuid'])
			return render_template('comments.html', title=title, url=articleurl, comments=struct, uname=name)
		else:
			return 'Does not exist'


#################################################################################

# show the user's profile and all the posts and comments s/he made
# OR show all the favorites that the user has saved
@app.route('/profiles/<uname>')
def profile(uname=None):
	return ''

#################################################################################
def signIn(r):
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
		flash('Invalid login')
		return ''



#################################################################################
if __name__ == '__main__':
	app.run(debug=True)