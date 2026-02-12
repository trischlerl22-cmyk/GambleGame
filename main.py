from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey") 

DB_FILE = "database.db"
TABLE_NAME = "Epstein_Contributors"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                country TEXT
            )
        """)
        conn.commit()
        conn.close()

init_db()

def check_user(username_to_check):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {TABLE_NAME} WHERE username = ?", (username_to_check,))
    user = c.fetchone()
    conn.close()
    if user:
        return True
    return False

def add_user(username, password, country):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"INSERT INTO {TABLE_NAME} (username, password, country) VALUES (?, ?, ?)",
                  (username, password, country))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/success/<int:score>')
def success(score):
    return render_template('success.html', result='success', score=score)


@app.route('/fail/<int:score>')
def fail(score):
    return render_template('fail.html', result='fail', score=score)

@app.route("/submit", methods=["POST"])
def submit():
    username = request.form.get("username")
    password = request.form.get("password")
    country = request.form.get("country")

    if not username or not password or not country:
        return jsonify({"status": "error", "message": "Missing fields"})

    if check_user(username):
        return jsonify({"status": "exists", "redirect": "/fail/0"}) 

    return jsonify({"status": "ok"})  


@app.route("/record_result", methods=["POST"])
def record_result():
    username = request.form.get("username")
    password = request.form.get("password")
    country = request.form.get("country")
    result = request.form.get("result") 

    if add_user(username, password, country):
        redirect_url = "/success/100" if result == "success" else "/fail/0"
        return jsonify({"status": "ok", "redirect": redirect_url})
    else:
        return jsonify({"status": "error", "message": "Could not record user"})


if __name__=='__main__':
    app.run(debug=True)
