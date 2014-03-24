from flask import Flask, render_template, session, flash, request, redirect, url_for
import secretKey, time, random, string, math
from dbStruct import DbStruct

app = Flask(__name__) 
app.secret_key = secretKey.key

database = DbStruct()

def generateURL():
	return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(25))

def signIn(r):
	user = r.form['user']
	pwd = r.form['pwd']
	login = database.checkLogIn(user, pwd)
	if login:
		session['uuid'] = login
		return user
	else:
		# Username is not in database, so do something about it
		# Form a response
		flash('Invalid login')
		return ''

@app.route('/')
def r():
	return redirect('/page/1')

# Add functionality to being already logged in
@app.route('/page/<number>', methods=['GET','POST'])
def index(number=0):
	if request.method == 'POST':	
		user = signIn(request)
		if number:
			return redirect('/page/%s' % number)
		else:
			return redirect('/')

	else:
		content = database.getArticles()
		totalContent = len(content)
		maxPages = math.ceil(totalContent/12)
		if number:
			num = int(number)
			accessContent = (num-1) * 12
		else:
			accessContent = 0
		content = content[accessContent:accessContent+12]
		rows = []
		k = len(content)

		for i in range(3):
			rows.append([])
			for j in range(4):
				if (i*4+j) < k:	
					rows[i].append(Entry(content[i*4+j]))
		t = False
		info = ''
		if 'uuid' in session:
			# generate content
			# rows variable
			
			t = True
			info = database.getUsername(session['uuid'])
		return render_template('index.html', user=t, uname = info, rows=rows, page=num,totalPages=maxPages)


# Pretty much all taken care of
@app.route('/logout')
def logout():
	session.pop('uuid', None)
	return redirect('/')


@app.route('/postArticle', methods=['GET','POST'])
def postArticle():
	if request.method == 'POST':
		if 'user' in request.form:
			user = signIn(request)
			return redirect('/postArticle')
		elif 'artUrl' in request.form:
			c = generateURL()
			u = database.getUsername(session['uuid'])
			args = (session['uuid'], u, request.form['artUrl'], time.time(), c, request.form['title'])
			state = database.addArticle(args)
			if state:
				return redirect('/')
			else:
				return '404'
	else:
		signedIn = False
		u = ''
		if 'uuid' in session:
			signedIn = True
			u = database.getUsername(session['uuid'])
		return render_template('postArticle.html', signedIn=signedIn, uname=u)

@app.route('/<commenturl>', methods=['GET','POST'])
def comment(commenturl):
	if request.method == 'POST':
		if 'user' in request.form:

			user = signIn(request)
			return redirect('/%s' % (commenturl))

		elif 'comment' in request.form:
			u = database.getUsername(session['uuid'])
			com = request.form['comment']
			t= time.time()
			database.addComment((commenturl, com, u, t))
			return redirect('/%s' % (commenturl))
	else:
		database.execute('select articleurl, comments, title from articles where comments=%s', (commenturl,))
		data = database.getOne()
		if data:
			title = data[2]
			articleurl = data[0]
			signedIn = False
			name = ''
			comms = database.getComments(commenturl)
			struct = [Comment(com[1],com[0]) for com in comms]
			if 'uuid' in session:
				signedIn = True
				name = database.getUsername(session['uuid'])
			return render_template('comments.html', title=title, url=articleurl, uname=name, signedIn=signedIn, comments=struct)
		else:
			return 'Does not exist'


@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		user = request.form['user']
		pwd = request.form['pwd']
		status = database.addUser(user, pwd)
		if status:
			database.execute('select (id) from users where username=%s', (user,))	
			uuid = database.getOne()[0]
			session['uuid'] = uuid
			return redirect('/')
		else:
			# TODO:
			# add error message
			return render_template('register.html')
	else:
		# render login form
		return render_template('register.html')

class Entry:
	def __init__(self, args):
		self.articleURL = args[0]
		self.title = args[2]
		self.commentURL = args[1]


class Comment:
	def __init__(self, u,t):
		self.user = u
		self.text = t


if __name__=="__main__":
	app.run()

