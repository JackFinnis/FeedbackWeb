from flask import Flask, render_template, request, redirect
from firebase_admin import credentials, firestore, initialize_app, storage
from models import *
import random
import string

flask_app = Flask(__name__)
cred = credentials.Certificate('creds.json')
firebase_app = initialize_app(cred)
db = firestore.client()
subjects = db.collection('subject')

def upload_photo(photo_url, public_id):
	client = storage.storage.Client.from_service_account_json('key.json')
	ref = client.get_bucket('logos').blob(public_id)
	ref.upload_from_filename(photo_url)
	return ref.public_url

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
	subject=Subject(1, 2, 'Apple', 'Please let us know how satisfied you are with your product and how we could have improved our customer service today.', '/static/jack.jpeg')
	return render_template('subject.html', feedbacks=[Feedback('Too expensive', '3', firestore.firestore.SERVER_TIMESTAMP)], subject=subject)

	subject = fetch_subject(private_id)
	docs = subjects.document(subject.public_id).collection('feedback').get()
	feedbacks = map(lambda x: Feedback.from_dict(x.to_dict()), docs)
	
	return render_template('subject.html', feedbacks=feedbacks, subject=subject)

@flask_app.route('/new')
def new_subject():
	return render_template('new_subject.html')

@flask_app.route('/new/submit', methods = ['POST'])
def submit_new_subject():
	return redirect(f'/subject/{1}')

	public_id = get_id()
	private_id = get_id()

	title = request.form['title']
	description = request.form['description']
	photo_url = request.form['logo']
	public_url = upload_photo(photo_url, public_id)

	new_topic = Subject(private_id, public_id, title, description, public_url)
	subjects.document(public_id).set(new_topic.to_dict())
	
	return redirect(f'/subject/{private_id}')

@flask_app.route('/send/<public_id>')
def send_feedback(public_id):
	subject=Subject(1, 2, 'Apple', 'Please let us know how satisfied you are with your product and how we could have improved our customer service today.', '/static/jack.jpeg')
	return render_template('send_feedback.html', subject=subject)

	subject = Subject.from_dict(subjects.document(public_id).get().to_dict())
	
	return render_template('send_feedback.html', public_id=public_id, title=title, description=description)

@flask_app.route('/send/submit/<public_id>', methods = ['POST'])
def submit_feedback(public_id):
	return render_template('submitted_feedback.html', public_id=2)

	feedback = request.form['feedback']
	feedback_id = get_id()
	feedback = Feedback(feedback, feedback_id, firestore.firestore.SERVER_TIMESTAMP)
	subjects.document(public_id).collection('feedback').document(feedback_id).set(feedback.to_dict())
    
	return render_template('submitted_feedback.html', public_id=public_id)

@flask_app.route('/delete_feedback/<feedback_id>/<private_id>')
def delete_feedback(feedback_id, private_id):
	return redirect(f"/subject/{1}")

	subject = fetch_subject(private_id)
	subjects.document(subject.public_id).collection('feedback').document(feedback_id).delete()

	return redirect(f"/subject/{private_id}")

@flask_app.errorhandler(404)
def handle_404(e):
	return render_template('404.html')

flask_app.run()