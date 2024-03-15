from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')