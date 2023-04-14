import logging

from flask import Flask, request, jsonify, redirect, render_template, request, session, flash, abort, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_appbuilder import AppBuilder, SQLA

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)


"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""
app.secret_key = 'super secret string' #Required for aunthentication

login_manager = LoginManager()
login_manager.init_app(app)

#Our mock database
users = {'student@ryerson.ca' : {'password' : 'secret'}}

#user class
class User(UserMixin) :
	pass
	
#Login manager loads user by email from mock database
@login_manager.user_loader
def user_loader(email) :
	if email not in users :
		return
	
	user = User()
	user.id = email
	return user
	
#Login manager loads user by email from form requesting username and password
@login_manager.request_loader
def request_loader(request) :
	email = request.form.get('email')
	if email not in users :
		return
		
	user = User()
	user.id = email
	return user
	

from app import views, models

@app.route('/list', methods = ['GET'])
def list_all() :
	result_set = db.session.query(models.User).all()
	return jsonify(result_set)
	
@app.route('/home')
def home() :
	return render_template('index.html')
		
@app.route('/deliverycost', methods = ['GET', 'POST'])
def calculate_cost() :
	if request.method == 'POST' :
		answer = {'status' : 'error'}
		try :
			weight = request.form.get('weight')
			distance = request.form.get('distance')
		
			query = db.session.query(models.User)
			weightCoefficientQuery = query.filter(models.User.name == 'weight')
			distanceCoefficientQuery = query.filter(models.User.name == 'distance')
			
			weightCoefficient = weightCoefficientQuery.first()
			distanceCoefficient = distanceCoefficientQuery.first()
		
			cost = float(weight) * weightCoefficient.value + float(distance) * distanceCoefficient.value
			
			answer = {'status' : 'success', 'data' : cost}
		except :
			answer = {'status' : 'error'}
			
		return jsonify(answer)
	else :
		return render_template('calculator.html')
		
@app.route('/login', methods = ['GET', 'POST'])
def login() :
	if request.method == 'GET' :
		return render_template('login.html')
	email = request.form['email']
	if email in users and request.form['password'] == users[email]['password'] :
		user = User()
		user.id = email
		login_user(user)
		return redirect(url_for('admin'))
		
	return 'Incorrect login'
	
		
@app.route('/admin')
@login_required
def admin() :
	#flash("You have been logged in!", "info")
	return render_template('admin.html')
	
	
#Logout from current session
@app.route('/logout')
def logout() :
	logout_user()
	return render_template('index.html')
	#return 'Logged Out'
	
#Handle unauthenticated users that access protected routes
@login_manager.unauthorized_handler
def unauthorized_handler() :
	return 'Unauthorized', 401
		
@app.route('/update', methods = ['GET', 'POST'])
def update() :
	if request.method == 'POST' :
		weight = request.form.get('weight')
		distance = request.form.get('distance')
	
		query = db.session.query(models.User)
		weightQuery = query.filter(models.User.name == 'weight')
		distanceQuery = query.filter(models.User.name == 'distance')
		weight_rows_changed = weightQuery.update({models.User.value:weight})
		distance_rows_changed = distanceQuery.update({models.User.value:distance})
		db.session.flush()
		db.session.commit()
		#flash("You have updated!", "info")
		return "Updated Successfully"
	
