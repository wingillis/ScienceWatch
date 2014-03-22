from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3

app = Flask(__name__) 

def getConn():
	connection = sqlite3.connect('scienceWatch.db')
	cursor = connection.cursor()
	return connection, cursor


@app.route('/')
def index():
	check = ''
	if 'username' in session:
		pass
	else:
		check = 'not '
	return render_template('index.html', var=check)

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		user = request.form['user']
		pwd = request.form['pwd']
		c, d = getConn()
		d.execute('insert into users (username, password) values (?,?)', (user, pwd))
		c.commit()
		d.close()
		session['username'] = user
		return redirect(url_for('index'))
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('username', None)
	return ''


if __name__=="__main__":
	app.secret_key = ')\xc1@V\xb6\x8d0K\xc8\x91\xc7\xff\xc4\x96\x91pK4\x9ft\xc7hs\xf5'
	app.run(host='127.0.0.1', debug=True)

	