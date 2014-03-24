from flask import Flask, render_template, session, request, redirect, url_for
import secretKey, time, random, string
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
	if login != None:
		session['uuid'] = login
		return user
	else:
		# Username is not in database, so do something about it
		# Form a response
		return ''




# Add functionality to being already logged in
@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':	
		user = signIn(request)
		
		return redirect('/')

	else:
		content = database.getFirst12Articles()
		rows = []
		for i in range(3):
			rows.append([])
			for j in range(4):	
				rows[i].append(Entry(content[i*4+j]))
		t = False
		info = ''
		if 'uuid' in session:
			# generate content
			# rows variable
			
			t = True
			info = database.getUsername(session['uuid'])
		return render_template('index.html', user=t, uname = info, rows=rows)


# Pretty much all taken care of
@app.route('/logout')
def logout():
	session.pop('uuid', None)
	return redirect(url_for('index'))


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
				return redirect(url_for('index'))
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
			return redirect(url_for('index'))
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

