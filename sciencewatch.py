from flask import Flask, render_template, session, request, redirect, url_for
import secretKey, psycopg2

app = Flask(__name__) 


@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		print(request.form['pwd'])
		# user = request.form['user']
		# pwd = request.form['pwd']
		# session['username'] = user
		return render_template('index.html')

	else:
		return render_template('index.html')


@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		# Give user an account, add them to database
		# redirect to home screen
		return redirect(url_for('index'))
	else:
		# render login form
		return render_template('register.html')

if __name__=="__main__":
	app.secret_key = secretKey.key
	app.run(host='127.0.0.1', debug=True)

