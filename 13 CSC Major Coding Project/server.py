from select import select
import sqlite3 as sql
import hashlib
import re
import os
from datetime import date, timedelta
import datetime
import time
from time import sleep
from flask import Flask, render_template, request, session

app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = os.urandom(24)

class opendb():
    def __init__(self, file_name):
        self.obj = sql.connect(file_name)
        self.cursor = self.obj.cursor()
    
    def __enter__(self):
        return self.cursor
    
    def __exit__(self, value, traceback, type):
        time.sleep(1)
        self.obj.commit()
        self.obj.close()

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/logout', methods=["GET", "POST"]) 
def logout():
    if 'logged_in' in session and session['logged_in']:
        session['logged_in'] = False
        session['user_id'] = "Invalid"
        return render_template('/message.html', message="You have been logged out")
    else:
        return render_template('/message.html', message="You are already not logged in")

@app.route('/login-page')
def login_page():
    return render_template('/login_page.html')

def login_success(user_name, last_login):
    with opendb('main.db') as c:
        c.execute("SELECT logins FROM users WHERE user_name = ?", (user_name,))
        c.fetchall()
        c.execute("UPDATE users SET logins = logins + 1 WHERE user_name = ?", (user_name,))
        c.execute("UPDATE users SET last_login = ?", (last_login,))

@app.route('/login', methods=["POST"])
def login_page_post():
    with opendb('main.db') as c:
        user_name = request.form['user_name']
        passkey = request.form['password']
        passkey_h = hashlib.sha256(passkey.encode('utf-8')).hexdigest()
        c.execute('SELECT * FROM users WHERE user_name=? AND password=?', (user_name, passkey_h)) 
        user_validation = c.fetchone()
        if user_validation:
            session['logged_in'] = True
            session['user_id'] = user_name
            last_login = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            login_success(user_name, last_login)
            return render_template('message.html', message="Login Success")
        else:
            session['logged_in'] = False
            session['user_id'] = "Invalid"
            return render_template('message.html', message="Login Failure")



#
@app.route('/signup-page') 
def signup_page():
    return render_template('/signup_page.html')
#
@app.route('/signup-page', methods=['POST'])
def signup_page_post():
    with opendb('main.db') as c:
        user_name = request.form['user_name']
        cursor = c.execute('SELECT user_name FROM users WHERE user_name=?', (user_name,))
        user_check = cursor.fetchall()
        now = datetime.datetime.now()
        date_created = now.strftime("%d/%m/%Y %H:%M")
        if user_check != 0: #checks if user exists
            email = request.form['email']
            passkey = request.form['password']
            logins=0
            passkey_h = hashlib.sha256(passkey.encode('utf-8')).hexdigest()
            c.execute('INSERT INTO users (user_name, email, password, logins, date_created, last_login) VALUES (?, ?, ?, ?, ?, ?)', (user_name, email, passkey_h, logins, date_created, "N/A"))
            return render_template('message.html', message="Sign Up success", herf="/menu")
        else:
            return render_template('message.html', message='Sign Up failure.')

@app.errorhandler(400)
def bad_request_error(error):
    return render_template('error_page.html',error_code="400", error_message="Bad Request"), 400
#Handles 401 errors - 
@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error_page.html',error_code="401", error_message="Unauthorized"), 401
#Handles 403 errors -
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error_page.html',error_code="403", error_message="Forbidden"), 403
#Handles 404 errors -
@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('error_page.html',error_code="404", error_message="Not Found"), 404
#Handles 405 errors -
@app.errorhandler(405)
def method_not_allowed_error(error):
    return render_template('error_page.html',error_code="405", error_message="Method Not Allowed"), 405
#Handles 503 errors -
@app.errorhandler(503)
def service_unavailable_error(error):
    return render_template('error_page.html',error_code="503", error_message="Service Unavailable"), 503

#Handles 500 errors - 
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error_page.html', error_code="500", error_message="Internal Server Error"), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
# remember to remove reloader=True and debug(True) when you move your
# application from development to a productive environment