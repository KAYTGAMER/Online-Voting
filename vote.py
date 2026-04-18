from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# DB connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="41589",
        database="online_voting"
    )

# Home
@app.route("/")
def home():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = connect_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO voters (username, password) VALUES (%s, %s)",
                (username, password)
            )
            db.commit()
            db.close()
            return redirect("/login")
        except:
            db.close()
            return "Username already exists"

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = connect_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT voter_id, has_voted FROM voters WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        db.close()

        if user:
            session["voter_id"] = user[0]
            session["has_voted"] = user[1]
            return redirect("/vote")
        else:
            return "Invalid credentials"

    return render_template("login.html")

# Vote
@app.route("/vote", methods=["GET", "POST"])
def vote():
    if "voter_id" not in session:
        return redirect("/login")

    db = connect_db()
    cursor = db.cursor()

    # Fetch candidates
    cursor.execute("SELECT candidate_id, name FROM candidates")
    candidates = cursor.fetchall()

    if request.method == "POST":
        if session.get("has_voted"):
            db.close()
            return "You already voted!"

        choice = request.form.get("candidate")

        if not choice:
            db.close()
            return "Please select a candidate"

        cursor.execute(
            "UPDATE candidates SET votes = votes + 1 WHERE candidate_id=%s",
            (choice,)
        )

        cursor.execute(
            "UPDATE voters SET has_voted=TRUE WHERE voter_id=%s",
            (session["voter_id"],)
        )

        db.commit()
        db.close()

        session["has_voted"] = True
        return redirect("/results")

    db.close()
    return render_template("vote.html", candidates=candidates)

# Results
@app.route("/results")
def results():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT name, votes FROM candidates")
    data = cursor.fetchall()
    db.close()

    return render_template("results.html", results=data)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Run
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)