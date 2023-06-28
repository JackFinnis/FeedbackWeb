import sqlite3
import uuid
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route("/")
def test():
	with sqlite3.connect("database.db") as db:
		cursor = db.cursor()
		cursor.execute("DROP TABLE feedback")
		sql = """
  		CREATE TABLE feedback (
			feedbackID TEXT,
   			feedback TEXT,
	  		publicID TEXT,
	 		timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
  		"""
		cursor.execute(sql)
		
		return "Feedback"

@app.route("/browse/<privateID>")
def browse(privateID):
	with sqlite3.connect("database.db") as db:
		cursor = db.cursor()
		sql = f"""
  		SELECT title, publicID
		FROM page
  		WHERE privateID='{privateID}'
  		"""
		cursor.execute(sql)
		(title, publicID) = cursor.fetchone()
		
		sql = f"""
  		SELECT feedbackID, feedback
		FROM feedback
  		WHERE publicID='{publicID}'
		"""
		cursor.execute(sql)
		feedbacks = cursor.fetchall()
		
		return render_template("browse.html", feedbacks=feedbacks, publicID=publicID, title=title, privateID=privateID)

@app.route("/start")
def get():
	return render_template("start.html")

@app.route("/submitStart", methods = ["POST"])
def submitGet():
	title = request.form["title"]
	description = request.form["description"]
	publicID = uuid.uuid4()
	privateID = uuid.uuid4()
	
	with sqlite3.connect("database.db") as db:
		cursor = db.cursor()
		sql = f"""
  		INSERT INTO page (title, description, publicID, privateID)
  		VALUES ('{title}', '{description}', '{publicID}', '{privateID}')
		"""
		cursor.execute(sql)
		
		return redirect(f"/browse/{privateID}")
		
@app.route("/send/<publicID>")
def send(publicID):
	with sqlite3.connect("database.db") as db:
		cursor = db.cursor()
		sql = f"""
  		SELECT title, description
		FROM page
  		WHERE publicID='{publicID}'
  		"""
		cursor.execute(sql)
		(title, description) = cursor.fetchone()
		
		return render_template("send.html", publicID=publicID, title=title, description=description)

@app.route("/submitSend/<publicID>", methods = ["POST"])
def submitFeedback(publicID):
    feedback = request.form["feedback"]
    feedbackID = uuid.uuid4()
	
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        sql = f"""
        INSERT INTO feedback (feedbackID, feedback, publicID)
		VALUES ('{feedbackID}', '{feedback}', '{publicID}')
  		"""
        cursor.execute(sql)
		
        return render_template("submitted.html", publicID=publicID)

@app.route("/deleteFeedback/<feedbackID>/<privateID>")
def deleteFeedback(feedbackID, privateID):
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        sql = f"""
        DELETE FROM feedback
		WHERE feedbackID='{feedbackID}'
  		"""
        cursor.execute(sql)
		
        return redirect(f"/browse/{privateID}")

app.run(host="0.0.0.0", port=5000, debug=True)