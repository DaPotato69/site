import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

# create database if it doesn't exist
conn = sqlite3.connect('articles.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS ARTICLES (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
cur.execute("CREATE TABLE IF NOT EXISTS PENDING (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
conn.close()

# get credentials from .env file
load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# create the Flask app, some other boilerplate code
app = Flask(__name__)
UPLOAD_FOLDER = "./static/blogs/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'many random bytes'

# home page
@app.route('/')
def home():
    # check if the user has just written an article
    written = request.args.get('written', default=0, type=int)
    # get all articles from the database
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ARTICLES")
    articles = cur.fetchall()
    conn.close()
    # display jinja2 template (its just html code)
    if written:
        return render_template('blog.html', articles=articles, written=1)
    else:
        return render_template('blog.html', articles=articles, written=0)

@app.route('/gallery')
def gallery():
    # display jinja2
    return render_template('gallery.html')

@app.route('/guide')
def guide():
    # display jinja2
    return render_template('guide.html')

@app.route('/legal')
def legal():
    # display jinja2
    return render_template('legal.html')

@app.route('/write')
def write():
    # display jinja2
    return render_template('write.html')

def allowed_file(filename):
    # check if the file is an image file
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/write', methods=['POST'])
def write_post():
    # get the form data
    article = dict(request.form)
    # check if the user has uploaded an image
    if 'file' not in request.files:
        flash('Please upload an image')
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
    if file and allowed_file(file.filename):
        extension = file.filename.split('.')[-1]
        filename = secure_filename(article['title'] + '.' + extension)
        # save the image to the server
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # save the article to the database
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    # add the date
    article["date"] = str(datetime.now().strftime("%d %B %Y"))
    cur.execute("INSERT INTO PENDING VALUES (?, ?, ?, ?, ?)", (article['title'], article['author'], article['date'], article['article'], filename))
    conn.commit()
    conn.close()
    # redirect to home page
    return redirect(url_for('home', written=1))

@app.route('/login')
def login():
    # display jinja2
    return render_template('login.html', incorrect=False)

@app.route('/login', methods=['POST'])
def login_post():
    # get entered credentials
    creds = dict(request.form)
    # check if the credentials are correct
    if creds['username'] == USERNAME and creds['password'] == PASSWORD:
        # redirect to admin page
        return redirect(url_for('admin', authenticated=1))
    else:
        # display jinja2, but with the incorrect flag set to True
        return render_template('login.html', incorrect=True)

@app.route('/admin')
def admin():
    # check the authenticated flag
    authenticated = request.args.get('authenticated', default=0, type=int)
    if authenticated:
        # get all pending articles
        conn = sqlite3.connect('articles.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM PENDING")
        articles = cur.fetchall()
        conn.close()
        # user is admin, send articles
        return render_template('admin.html', authenticated=authenticated, articles=articles)
    else:
        # not authenticated
        return render_template('admin.html', authenticated=authenticated)

# no html attached to this route
@app.route('/admin/accept/<article>')
def admin_post_accept(article):
    # remove from pending, add to articles
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM PENDING WHERE title=?", (article,))
    article = cur.fetchall()[0]
    cur.execute("INSERT INTO ARTICLES VALUES (?, ?, ?, ?, ?)", article)
    cur.execute("DELETE FROM PENDING WHERE title=?", (article[0],))
    conn.commit()
    conn.close()
    # go back to admin page
    return redirect(url_for('admin', authenticated=1))

# no html attached to this route
@app.route('/admin/reject/<article>')
def admin_post_reject(article):
    # remove from pending
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM PENDING WHERE title=?", (article,))
    article = cur.fetchall()[0]
    cur.execute("DELETE FROM PENDING WHERE title=?", (article[0],))
    conn.commit()
    conn.close()
    # go back to admin page
    return redirect(url_for('admin', authenticated=1))