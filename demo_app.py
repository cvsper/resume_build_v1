from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response, jsonify, flash
from resume.resume_generator import generate_resume, generate_cover_letter, generate_interview_qa
import tempfile
from weasyprint import HTML
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from datetime import datetime
from flask_migrate import Migrate
import requests
import logging
from werkzeug.routing import BuildError

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "default_id")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "default_key")

app = Flask(__name__)
app_secret = os.getenv("SECRET_KEY", "test_secret_key_for_demo")
app.secret_key = app_secret

# Use SQLite for demo
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))
    preferred_template = db.Column(db.String(50), default='classic')
    profile_pic = db.Column(db.String(200), default='default.jpg')

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    template = db.Column(db.String(50), default='classic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('resumes', lazy=True))

class CoverLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('cover_letters', lazy=True))

app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        name = request.form.get('name', '')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return render_template('register.html')
        
        new_user = User(email=email, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    cover_letters = CoverLetter.query.filter_by(user_id=current_user.id).all()
    interview_qa_list = session.get('interview_qa_list', [])
    return render_template('dashboard.html', 
                           resumes=resumes, 
                           cover_letters=cover_letters, 
                           interview_qa_list=interview_qa_list)

@app.route('/resumes')
@login_required
def resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    return render_template('resumes.html', resumes=resumes, current_user=current_user, active_page='resumes')

@app.route('/cover_letters')
@login_required
def cover_letters():
    cover_letters = CoverLetter.query.filter_by(user_id=current_user.id).all()
    return render_template('cover_letters.html', cover_letters=cover_letters, current_user=current_user, active_page='cover_letters')

@app.route('/interview_qa', methods=['GET', 'POST'])
@login_required
def interview_qa():
    interview_qa_list = session.get('interview_qa_list', [])
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        if job_title:
            qa_content = f"Sample Q&A for {job_title}"  # Simplified for demo
            interview_qa_list.append({'job_title': job_title, 'qa': qa_content})
            session['interview_qa_list'] = interview_qa_list
            session.modified = True
            return redirect(url_for('interview_qa'))
    return render_template('interview_qa.html', interview_qa_list=interview_qa_list, current_user=current_user, active_page='interview_qa')

@app.route('/create_cover_letter')
@login_required
def create_cover_letter():
    return render_template('create_cover_letter.html', current_user=current_user, active_page='cover_letters')

@app.route('/resume_creation_menu')
@login_required
def resume_creation_menu():
    return render_template('resume_creation_menu.html', current_user=current_user, active_page='resumes')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting demo app on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
