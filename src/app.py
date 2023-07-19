from flask import Flask, render_template, request, redirect, abort
from firebase_admin import credentials, firestore, initialize_app, storage
from google.cloud.firestore_v1.base_query import FieldFilter
from models import *
import random
import string

# Configure Firebase
creds = credentials.Certificate('creds.json')
firebase_app = initialize_app(creds, {
	'storageBucket': 'feedback-5331f.appspot.com'
})

bucket = storage.bucket()
db = firestore.client()
subjects = db.collection('subject')

# Helper Functions
def upload_file(file, id):
	ref = bucket.blob(id)
	ref.upload_from_file(file)
	ref.make_public()
	return ref.public_url

def fetch_subject_private(private_id):
	docs = subjects.where(filter=FieldFilter('private_id', '==', private_id)).stream()
	doc = next(docs, None)
	if not doc: abort(404); return
	return Subject.from_dict(doc.to_dict())

def fetch_subject_public(public_id):
	doc = subjects.document(public_id).get()
	if not doc.exists: abort(404); return
	return Subject.from_dict(doc.to_dict())

def get_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Configure Flask routing
flask_app = Flask(__name__)

@flask_app.route('/')
def root():
	return redirect('/new')

@flask_app.route('/new')
def subject_new():
	return render_template('new_subject.html')

@flask_app.route('/new', methods=['POST'])
def subject_new_submit():
	title = request.form['title']
	description = request.form['description']
	logo = request.files['logo']

	public_id = get_id()
	private_id = get_id()
	public_url = None
	if logo.filename:
		public_url = upload_file(logo, public_id)

	new_subject = Subject(private_id, public_id, title, description, public_url, live=True, shown_save_alert=False)
	subjects.document(public_id).set(new_subject.to_dict())
	
	return redirect(f'/subject/{private_id}')

@flask_app.route('/subject/<private_id>')
def subject(private_id):
	subject = fetch_subject_private(private_id)
	docs = subjects.document(subject.public_id).collection('feedback').order_by('timestamp', direction=firestore.firestore.Query.DESCENDING).get()
	feedbacks = list(map(lambda x: Feedback.from_dict(x.to_dict()), docs))

	if not subject.shown_save_alert:
		subject.shown_save_alert = True
		subjects.document(subject.public_id).set(subject.to_dict())
		subject.shown_save_alert = False

	return render_template('subject.html', feedbacks=feedbacks, subject=subject)

@flask_app.route('/subject/<private_id>/delete')
def subject_delete(private_id):
	subject = fetch_subject_private(private_id)
	subjects.document(subject.public_id).delete()
	if subject.photo_url:
		bucket.blob(subject.public_id).delete()

	return render_template('subject_deleted.html')

@flask_app.route('/subject/<private_id>/toggle_live')
def subject_toggle_live(private_id):
	subject = fetch_subject_private(private_id)
	subject.live = not subject.live
	subjects.document(subject.public_id).set(subject.to_dict())

	return redirect(f'/subject/{private_id}')

@flask_app.route('/subject/<private_id>/feedback/<feedback_id>/delete')
def feedback_delete(private_id, feedback_id):
	subject = fetch_subject_private(private_id)
	subjects.document(subject.public_id).collection('feedback').document(feedback_id).delete()

	return redirect(f'/subject/{private_id}')

@flask_app.route('/send/<public_id>')
def feedback_send(public_id):
	subject = fetch_subject_public(public_id)
	
	return render_template('send_feedback.html', subject=subject, submitted=False)

@flask_app.route('/send/<public_id>', methods=['POST'])
def feedback_submit(public_id):
	subject = fetch_subject_public(public_id)
	if not subject.live:
		return redirect(f'/send/{public_id}')

	feedback = request.form['feedback']
	feedback_id = get_id()

	feedback = Feedback(feedback, feedback_id, firestore.firestore.SERVER_TIMESTAMP)
	subjects.document(public_id).collection('feedback').document(feedback_id).set(feedback.to_dict())
    
	return render_template('send_feedback.html', subject=subject, submitted=True)

@flask_app.errorhandler(404)
def error_404(e):
	return render_template('error_404.html')

flask_app.run()