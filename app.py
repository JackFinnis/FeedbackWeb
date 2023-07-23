from flask import Flask, render_template, request, redirect, abort
from werkzeug.datastructures import FileStorage
from firebase_admin import firestore, credentials, initialize_app, storage
from google.cloud.firestore_v1.base_query import FieldFilter
from creds import creds_file
from io import BytesIO

from models import *

# Configure Firebase
creds = credentials.Certificate(creds_file)
firebase_app = initialize_app(creds, {
	'storageBucket': 'feedback-5331f.appspot.com'
})

bucket = storage.bucket()
db = firestore.client()
subjects = db.collection('subject')

# Firebase helpers
def upload_image(file: FileStorage, id: str) -> str:
	image = Image.open(file)
	image = ImageOps.exif_transpose(image)
	image = resize_image(image, 300)

	temp = BytesIO()
	image.save(temp, "jpeg", optimize=True, quality=50)
	temp.seek(0)

	ref = bucket.blob(id)
	ref.upload_from_file(temp, content_type='image/jpeg')
	ref.make_public()

	return ref.public_url

def fetch_subject_private(private_id: str) -> Subject:
	docs = subjects.where(filter=FieldFilter('private_id', '==', private_id)).stream()
	doc = next(docs, None)
	if not doc: abort(404); return
	return Subject.from_dict(doc.to_dict())

def fetch_subject_public(public_id) -> Subject:
	doc = subjects.document(public_id).get()
	if not doc.exists: abort(404); return
	return Subject.from_dict(doc.to_dict())

# Configure Flask routing
flask_app = Flask(__name__)

@flask_app.route('/')
def root():
	return render_template('how_it_works.html')

@flask_app.route('/create')
def create_subject():
	return render_template('create_subject.html')

@flask_app.route('/create', methods=['POST'])
def create_subject_submit():
	title = request.form['title']
	description = request.form['description']
	logo = request.files['logo']

	private_id = get_id()
	public_id = get_id()
	public_url = None
	if logo.filename:
		public_url = upload_image(logo, public_id)

	new_subject = Subject(private_id, public_id, title, description, public_url, live=True)
	subjects.document(public_id).set(new_subject.to_dict())
	
	return redirect(f'/{private_id}', code=307)

@flask_app.route('/<private_id>', methods=['POST'])
def subject_created(private_id: str):
	return render_template('subject_created.html', private_id=private_id)

@flask_app.route('/<private_id>')
def subject(private_id: str):
	subject = fetch_subject_private(private_id)
	docs = subjects.document(subject.public_id).collection('feedback').order_by('timestamp', direction=firestore.firestore.Query.DESCENDING).get()
	feedbacks = list(map(lambda x: Feedback.from_dict(x.to_dict()), docs))

	return render_template('subject.html', feedbacks=feedbacks, subject=subject)

@flask_app.route('/<private_id>/delete')
def subject_delete(private_id: str):
	subject = fetch_subject_private(private_id)
	subjects.document(subject.public_id).delete()
	if subject.photo_url:
		bucket.blob(subject.public_id).delete()

	return render_template('subject_deleted.html')

@flask_app.route('/<private_id>/toggle_live')
def subject_toggle_live(private_id: str):
	subject = fetch_subject_private(private_id)
	subject.live = not subject.live
	subjects.document(subject.public_id).set(subject.to_dict())

	return redirect(f'/{private_id}')

@flask_app.route('/<private_id>/description', methods=['POST'])
def subject_update_description(private_id: str):
	subject = fetch_subject_private(private_id)
	description = request.form['description']
	subject.description = description
	subjects.document(subject.public_id).set(subject.to_dict())

	return redirect(f'/{private_id}')

@flask_app.route('/<private_id>/feedback/<feedback_id>/delete')
def feedback_delete(private_id: str, feedback_id: str):
	subject = fetch_subject_private(private_id)
	subjects.document(subject.public_id).collection('feedback').document(feedback_id).delete()

	return redirect(f'/{private_id}')

@flask_app.route('/send/<public_id>')
def send_feedback(public_id: str):
	subject = fetch_subject_public(public_id)
	
	return render_template('send_feedback.html', subject=subject, submitted=False)

@flask_app.route('/send/<public_id>', methods=['POST'])
def send_feedback_submit(public_id: str):
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