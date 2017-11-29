from flask import Flask, render_template, request, url_for, redirect, flash, session
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import tweepy
import MySQLdb as database
import json

app = Flask(__name__)
app.secret_key = "thisiskey"

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])
    
@app.route('/dashboard')
def dashboard():
    if  session.get('username'):  
      return render_template('dashboard.html')
    else:
      return render_template('index.html')
      
@app.route('/')
def homepage():
    if session.get('username'):
        return render_template('dashboard.html')
    else:
        return render_template("index.html")

@app.route('/login_page', methods=["GET","POST"])
def login_page():

    error = ''
    try:
        if request.method == "POST":
		
            attempted_username = request.form['username']
            attempted_password = request.form['password']

            #flash(attempted_username)
            #flash(attempted_password)

            if attempted_username == "admin" and attempted_password == "password":
                session['username'] = attempted_username
                return redirect(url_for('dashboard'))
				
            else:
                error = "Invalid credentials. Try Again."

        return redirect(url_for('homepage'))

    except Exception as e:
        #flash(e)
        return redirect(url_for('homepage'))

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            #password = sha256_crypt.encrypt((str(form.password.data)))
            password = form.password.data
            c, conn = connection()

            #x = c.execute("SELECT * FROM users WHERE username = (%s)",
            #              (username))

            #kif int(x) > 0:
             #   flash("That username is already taken, please choose another")
              #  return render_template('register.html', form=form)

            #else:
            c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            ((username), (password), (email)))
                
            conn.commit()
            flash("Thanks for registering!")
            c.close()
            conn.close()
            gc.collect()

            session['logged_in'] = True
            session['username'] = username

            return redirect(url_for('homepage'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))

consumer_key = 'foPgt4FTfPNPffEIDULlNdN45'
consumer_secret = 'xCO7Lcjh22ORCF7E1i8X602gwzc8peun203iDUO4HBKLKxNBnT'
callback = 'http://139.59.70.77/callback'
@app.route('/auth')
def auth():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    url = auth.get_authorization_url()
    session['request_token'] = auth.request_token
    return redirect(url)

@app.route('/callback')
def twitter_callback():
    c, conn = connection()
    request_token = session['request_token']
    del session['request_token']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.request_token = request_token
    verifier = request.args.get('oauth_verifier')
    auth.get_access_token(verifier)
    username = auth.get_username()
    user = tweepy.API(auth)
    try:
        t01 = user.user_timeline()[0]
        myId = t01.id 
    except tweepy.TweepError, e:
        myId = 0

    c.execute("INSERT INTO twitter_users (displayName ,access_token, access_secret, lasttweet) VALUES (%s ,%s, %s, %s)",
    ((username) ,(auth.access_token), (auth.access_token_secret), (myId)))
    conn.commit()
    c.close()
    conn.close()
    gc.collect()

    return render_template('redirect.html')


      
@app.route('/signout')
def signout():
    if session.get('username'):
       session.pop('username',None)
    return render_template("index.html")
    
@app.route('/getusers',methods=['GET'])
def users():
    if session.get('username'):
       c,conn=connection()
       
       c.execute("select * from twitter_users")
       row = c.fetchone()
       user=[]
       i=0
       while row is not None:
          data=(row[1],row[2])
          user.append(data)
          row = c.fetchone()
          
       c.close()
       conn.close()
       return  json.dumps(user)
    else:
       return redirect(url_for('homepage'))


if __name__ == "__main__":
    app.run()