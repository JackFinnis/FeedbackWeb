from flask import Flask, render_template, request, redirect
from firebase_admin import credentials, firestore, initialize_app
from models import *
from uuid import uuid4

# change templates to snake not camel case

flask_app = Flask(__name__)
cred = credentials.Certificate('key.json')
firebase_app = initialize_app(cred)
db = firestore.client()
topics = db.collection('topic')

def fetch_topic(private_id):
	docs = topics.where('private_id', '==', private_id)
	return Topic.from_dict(next(docs).to_dict())

@flask_app.route('/')
def root():
	redirect('new')

@flask_app.route('/topic/<private_id>')
def topic(private_id):
	topic = fetch_topic(private_id)
	title = topic.title
	public_id = topic.public_id
	docs = topics.get(public_id).collection('comments').stream()
	comments = map(lambda x: Comment.from_dict(x.to_dict()), docs)
	
	return render_template('browse.html', comments=comments, public_id=public_id, title=title, private_id=private_id)

@flask_app.route('/new')
def new_topic():
	return render_template('new_topic.html')

@flask_app.route('/new/submit', methods = ['POST'])
def submit_new_topic():
	title = request.form['title']
	description = request.form['description']
	public_id = uuid4()
	private_id = uuid4()
	new_topic = Topic(private_id=private_id, public_id=public_id, title=title, description=description)
	topics.document(public_id).set(new_topic)
	
	return redirect(f'/topic/{private_id}')

@flask_app.route('/send/<public_id>')
def send_feedback(public_id):
	topic = Topic.from_dict(topics.document(public_id).get().to_dict())
	
	return render_template('send_feedback.html', publicID=topic.publicID, title=topic.title, description=topic.description)

@flask_app.route('/send/submit/<public_id>', methods = ['POST'])
def submit_feedback(public_id):
	comment = request.form['feedback']
	comment_id = uuid4()
	comment = Comment(comment=comment, comment_id=comment_id)
	topics.document(public_id).collection('comments').document(comment_id).set(comment.to_dict())
    
	return render_template('submitted_feedback.html', public_id=public_id)

@flask_app.route('/deleteComment/<comment_id>/<private_id>')
def delete_comment(comment_id, private_id):
	topic = fetch_topic(private_id)
	topics.document(topic.public_id).collection('comments').document(comment_id).delete()

	return redirect(f"/topic/{private_id}")

flask_app.run()