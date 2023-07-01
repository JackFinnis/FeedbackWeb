from flask import Flask, render_template, request, redirect
from firebase_admin import credentials, firestore, initialize_app
from models import *
import random
import string

flask_app = Flask(__name__)
cred = credentials.Certificate('key.json')
firebase_app = initialize_app(cred)
db = firestore.client()
subjects = db.collection('subject')

def fetch_subject(private_id):
	docs = subjects.where('private_id', '==', private_id).stream()
	return Subject.from_dict(next(docs).to_dict())

def get_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@flask_app.route('/')
def root():
	return redirect('/new')

@flask_app.route('/subject/<private_id>')
def subject(private_id):
	subject = fetch_subject(private_id)
	title = subject.title
	public_id = subject.public_id
	docs = subjects.document(public_id).collection('feedback').get()
	feedbacks = map(lambda x: Feedback.from_dict(x.to_dict()), docs)
	
	return render_template('subject.html', feedbacks=feedbacks, public_id=public_id, title=title, private_id=private_id)

@flask_app.route('/new')
def new_subject():
	return render_template('new_subject.html')

@flask_app.route('/new/submit', methods = ['POST'])
def submit_new_subject():
	title = request.form['title']
	description = request.form['description']
	public_id = get_id()
	private_id = get_id()
	new_topic = Subject(private_id, public_id, title, description)
	subjects.document(public_id).set(new_topic.to_dict())
	
	return redirect(f'/subject/{private_id}')

@flask_app.route('/send/<public_id>')
def send_feedback(public_id):
	subject = Subject.from_dict(subjects.document(public_id).get().to_dict())
	publicID = subject.public_id
	title = subject.title
	description = subject.description
	
	return render_template('send_feedback.html', public_id=public_id, title=title, description=description)

@flask_app.route('/send/submit/<public_id>', methods = ['POST'])
def submit_feedback(public_id):
	feedback = request.form['feedback']
	feedback_id = get_id()
	feedback = Feedback(feedback, feedback_id)
	subjects.document(public_id).collection('feedback').document(feedback_id).set(feedback.to_dict())
    
	return render_template('submitted_feedback.html', public_id=public_id)

@flask_app.route('/delete_feedback/<feedback_id>/<private_id>')
def delete_feedback(feedback_id, private_id):
	subject = fetch_subject(private_id)
	subjects.document(subject.public_id).collection('feedback').document(feedback_id).delete()

	return redirect(f"/subject/{private_id}")

flask_app.run()