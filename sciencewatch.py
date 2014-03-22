from flask import Flask, render_template, session, request, redirect, url_for
import secretKey, psycopg2

app = Flask(__name__) 


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		user = request.form['user']
		pwd = request.form['pwd']
		session['username'] = user
		return redirect(url_for('index'))
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('username', None)
	return ''


if __name__=="__main__":
	app.secret_key = secretKey.key
	app.run(host='127.0.0.1', debug=True)

