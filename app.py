import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

conn = sqlite3.connect('articles.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS ARTICLES (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
conn.close()

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
    cur.execute("INSERT INTO ARTICLES VALUES (?, ?, ?, ?, ?)", (article['title'], article['author'], article['date'], article['article'], filename))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))