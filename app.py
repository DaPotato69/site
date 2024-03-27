import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

conn = sqlite3.connect('articles.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS ARTICLES (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
cur.execute("CREATE TABLE IF NOT EXISTS PENDING (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
conn.close()

load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

app = Flask(__name__)
UPLOAD_FOLDER = "./static/blogs/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'many random bytes'

@app.route('/')
def home():
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ARTICLES")
    articles = cur.fetchall()
    #print(articles)
    conn.close()
    return render_template('blog.html', articles=articles)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/legal')
def legal():
    return render_template('legal.html')

@app.route('/write')
def write():
    return render_template('write.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/write', methods=['POST'])
def write_post():
    article = dict(request.form)

    if 'file' not in request.files:
        flash('Please upload an image')
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
    if file and allowed_file(file.filename):
        extension = file.filename.split('.')[-1]
        filename = secure_filename(article['title'] + '.' + extension)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    article["date"] = str(datetime.now().strftime("%d %B %Y"))
    #print(article['title'])
    cur.execute("INSERT INTO PENDING VALUES (?, ?, ?, ?, ?)", (article['title'], article['author'], article['date'], article['article'], filename))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/login')
def login():
    return render_template('login.html', incorrect=False)

@app.route('/login', methods=['POST'])
def login_post():
    creds = dict(request.form)
    if creds['username'] == USERNAME and creds['password'] == PASSWORD:
        return redirect(url_for('admin', authenticated=1))
    else:
        return render_template('login.html', incorrect=True)

@app.route('/admin')
def admin():
    authenticated = request.args.get('authenticated', default=0, type=int)
    #print(authenticated)
    if authenticated:
        conn = sqlite3.connect('articles.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM PENDING")
        articles = cur.fetchall()
        conn.close()
        return render_template('admin.html', authenticated=authenticated, articles=articles)
    else:
        return render_template('admin.html', authenticated=authenticated)

@app.route('/admin/accept/<article>')
def admin_post_accept(article):
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM PENDING WHERE title=?", (article,))
    article = cur.fetchall()[0]
    cur.execute("INSERT INTO ARTICLES VALUES (?, ?, ?, ?, ?)", article)
    cur.execute("DELETE FROM PENDING WHERE title=?", (article[0],))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', authenticated=1))

@app.route('/admin/reject/<article>')
def admin_post_reject(article):
    conn = sqlite3.connect('articles.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM PENDING WHERE title=?", (article,))
    article = cur.fetchall()[0]
    cur.execute("DELETE FROM PENDING WHERE title=?", (article[0],))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', authenticated=1))