import sqlite3
conn = sqlite3.connect('articles.db')
cur = conn.cursor()
cur.execute("DROP TABLE ARTICLES")
cur.execute("DROP TABLE PENDING")
cur.execute("CREATE TABLE ARTICLES (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
cur.execute("CREATE TABLE PENDING (title VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, published VARCHAR(255) NOT NULL, article TEXT NOT NULL, imgname VARCHAR(255) NOT NULL)")
conn.close()