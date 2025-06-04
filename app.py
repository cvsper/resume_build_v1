from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response, jsonify, flash
from resume.resume_generator import generate_resume, generate_cover_letter, generate_interview_qa
import tempfile
from weasyprint import HTML
import stripe
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from datetime import datetime
from flask_migrate import Migrate
import requests
import fitz  # PyMuPDF
import logging
from werkzeug.routing import BuildError





ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

app = Flask(__name__)
app_secret = os.getenv("SECRET_KEY")
if not app_secret:
    raise RuntimeError("SECRET_KEY environment variable not set. Please set it in your environment or Render dashboard.")
app.secret_key = app_secret

stripe_secret = os.getenv("STRIPE_SECRET_KEY")
if not stripe_secret:
    raise RuntimeError("STRIPE_SECRET_KEY environment variable not set. Please set it in your environment or Render dashboard.")
stripe.api_key = stripe_secret

supabase_db_url = os.getenv('SUPABASE_DB_URL')
if not supabase_db_url:
    raise RuntimeError('SUPABASE_DB_URL environment variable not set. Get your connection string from your Supabase project.')
app.config['SQLALCHEMY_DATABASE_URI'] = supabase_db_url
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Old SQLite, now disabled

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={'access_type': 'offline', 'prompt': 'consent'},
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

class CoverLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(150))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('cover_letters', lazy=True))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150))
    oauth_provider = db.Column(db.String(50))
    password = db.Column(db.String(256), nullable=False)
    preferred_template = db.Column(db.String(50), default='classic')
    profile_pic = db.Column(db.String(200), default='default.jpg')
    subscription = db.Column(db.String(50), default='Free')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    template = db.Column(db.String(50), default='classic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('resumes', lazy=True))

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150))
    company = db.Column(db.String(150))
    location = db.Column(db.String(150))
    url = db.Column(db.String(300))
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('saved_jobs', lazy=True))

app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/resumes', methods=['GET'])
@login_required
def get_resumes_api():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    data = [{
        'id': r.id,
        'title': r.title,
        'content': r.content,
        'template': r.template,
        'created_at': r.created_at.isoformat()
    } for r in resumes]
    return jsonify(data)

@app.route('/api/resumes', methods=['POST'])
@login_required
def create_resume_api():
    data = request.json
    new_resume = Resume(
        user_id=current_user.id,
        title=data['title'],
        content=data['content'],
        template=data.get('template', 'classic')
    )
    db.session.add(new_resume)
    db.session.commit()
    return jsonify({'message': 'Resume created', 'id': new_resume.id}), 201

@app.route('/api/resumes/<int:resume_id>', methods=['DELETE'])
@login_required
def delete_resume_api(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(resume)
    db.session.commit()
    return jsonify({'message': 'Resume deleted'})

@app.route('/api/cover-letters', methods=['GET'])
@login_required
def get_cover_letters_api():
    letters = CoverLetter.query.filter_by(user_id=current_user.id).all()
    data = [{'id': l.id, 'job_title': l.job_title, 'content': l.content, 'created_at': l.created_at.isoformat()} for l in letters]
    return jsonify(data)

@app.route('/api/cover-letters', methods=['POST'])
@login_required
def create_cover_letter_api():
    data = request.json
    content = generate_cover_letter(current_user.name, current_user.email, data['job_title'], data['description'])
    letter = CoverLetter(user_id=current_user.id, job_title=data['job_title'], content=content)
    db.session.add(letter)
    db.session.commit()
    return jsonify({'message': 'Cover letter created', 'id': letter.id}), 201


@app.route('/api/interview-qa', methods=['POST'])
@login_required
def generate_interview_qa_api():
    data = request.json
    job_title = data['job_title']
    qa_content = generate_interview_qa(job_title)
    return jsonify({'qa': qa_content})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            return 'Email already registered!'
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
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
        return 'Invalid credentials'
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
    # Defensive: filter out any cover letters with missing, None, or invalid id
    valid_cover_letters = []
    for cl in cover_letters:
        if isinstance(getattr(cl, 'id', None), int) and getattr(cl, 'id', None) > 0:
            valid_cover_letters.append(cl)
        else:
            app.logger.warning(f"[dashboard] Skipping cover letter with invalid id: {getattr(cl, 'id', None)}")
    app.logger.info(f"[dashboard] Rendering cover_letters: {[cl.id for cl in valid_cover_letters]}")
    interview_qa_list = session.get('interview_qa_list', [])
    # Defensive: always pass resumes as a list
    if resumes is None:
        resumes = []
    return render_template('dashboard.html', 
                           resumes=resumes, 
                           cover_letters=valid_cover_letters, 
                           interview_qa_list=interview_qa_list)



# Cover Letter Creation Route
@app.route('/create-cover-letter', methods=['GET', 'POST'])
@login_required
def create_cover_letter():
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        description = request.form.get('description')
        name = current_user.name
        email = current_user.email
        
        # Use GPT to generate cover letter content
        content = generate_cover_letter(name, email, job_title, description)
        
        new_cover_letter = CoverLetter(
            user_id=current_user.id,
            job_title=job_title,
            content=content
        )
        db.session.add(new_cover_letter)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('create_cover_letter.html')

@app.route('/create-resume', methods=['GET', 'POST'])
@login_required
def create_resume():
    if request.method == 'POST':
        logging.debug('Create resume POST request received.')
        # Use a default title since the form field was removed
        title = f"Resume - {current_user.name or current_user.email}"
        experience = request.form.get('content', '').strip()
        if not experience:
            # Show a user-friendly error if content is missing
            error_message = 'Please enter your experience or resume content.'
            return render_template('create_resume.html', error_message=error_message)
        template = request.form.get('template', 'classic')
        name = request.form.get('name', '')
        # Capitalize the first letter of each word in the name
        name = ' '.join([part.capitalize() for part in name.split()])
        content = generate_resume(name, '', current_user.email, title, experience)
        new_resume = Resume(user_id=current_user.id, title=title, content=content, template=template)
        db.session.add(new_resume)
        db.session.commit()
        # Generate thumbnail after saving
        rendered_html = render_template(f"resume_templates/{template}.html", resume=new_resume)
        try:
            generate_resume_thumbnail(new_resume.id, rendered_html)
        except Exception as e:
            logging.error(f'Thumbnail generation failed: {e}')
        logging.debug('Redirecting to preview_resume.')
        return redirect(url_for('resumes'))
    logging.debug('Rendering create_resume.html template.')
    return render_template('create_resume.html')

@app.route('/edit-resume/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    if request.method == 'POST':
        resume.title = request.form['title']
        resume.content = request.form['content']
        resume.template = request.form.get('template', 'classic')
        db.session.commit()
        # Generate thumbnail after editing
        rendered_html = render_template(f"resume_templates/{resume.template}.html", resume=resume)
        try:
            generate_resume_thumbnail(resume.id, rendered_html)
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
        return redirect(url_for('dashboard'))
    return render_template('edit_resume.html', resume=resume)

@app.route('/delete-resume/<int:resume_id>')
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(resume)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        preferred_template = request.form.get('preferred_template')
        file = request.files.get('profile_pic')

        current_user.name = name
        current_user.preferred_template = preferred_template

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.profile_pic = filename

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('profile.html', user=current_user)


@app.route('/preview-resume', defaults={'resume_id': None})
@app.route('/preview-resume/<int:resume_id>')
@login_required
def preview_resume(resume_id):
    resume = Resume.query.get(resume_id) if resume_id else Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    if not resume or resume.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    return render_template(f"resume_templates/{resume.template}.html", resume=resume)

@app.route('/find-jobs', methods=['GET', 'POST'])
@login_required
def find_jobs():
    keyword = request.form.get('keyword', '')
    location = request.form.get('location', '')
    country = 'us'  # or 'gb', 'ca', etc.
    
    # Build API URL
    api_url = f'https://api.adzuna.com/v1/api/jobs/{country}/search/1'
    params = {
        'app_id': '8015aa6c',
        'app_key': 'b704fa323f3ffea50f9c20bca03c5caf',
        'what': keyword,
        'where': location,
        'results_per_page': 10,
        'content-type': 'application/json'
    }
    response = requests.get(api_url, params=params)
    
    job_listings = []
    if response.status_code == 200:
        data = response.json()
        job_listings = [{
            'title': job.get('title', 'N/A'),
            'company': job.get('company', {}).get('display_name', 'N/A'),
            'location': job.get('location', {}).get('display_name', 'N/A'),
            'url': job.get('redirect_url', '#'),
            'description': job.get('description', '')
        } for job in data.get('results', [])]
    
    saved_jobs = SavedJob.query.filter_by(user_id=current_user.id).all()
    return render_template('find_jobs.html', jobs=job_listings, saved_jobs=saved_jobs)

@app.route('/save-job', methods=['POST'])
@login_required
def save_job():
    title = request.form['title']
    company = request.form['company']
    location = request.form['location']
    url = request.form['url']

    existing = SavedJob.query.filter_by(user_id=current_user.id, url=url).first()
    if not existing:
        new_saved = SavedJob(
            user_id=current_user.id,
            title=title,
            company=company,
            location=location,
            url=url
        )
        db.session.add(new_saved)
        db.session.commit()

    return redirect(url_for('find_jobs'))


@app.route('/generate-interview/<job_title>')
@login_required
def generate_interview_for_job(job_title):
    qa_content = generate_interview_qa(job_title)
    
    # Get current list or initialize
    interview_qa_list = session.get('interview_qa_list', [])
    
    # Append and reassign
    interview_qa_list.append({'job_title': job_title, 'qa': qa_content})
    session['interview_qa_list'] = interview_qa_list
    
    # Explicitly mark the session as modified
    session.modified = True
    
    return redirect(url_for('dashboard'))



@app.route('/clear-interview-qa')
@login_required
def clear_interview_qa():
    session.pop('interview_qa_list', None)
    return redirect(url_for('dashboard'))



@app.route('/create-resume/<job_title>')
@login_required
def create_resume_for_job(job_title):
    # Redirect to create resume with job title pre-filled (optional: use a session or GET param)
    session['prefill_job_title'] = job_title
    return redirect(url_for('create_resume'))

@app.route('/create-cover-letter/<job_title>')
@login_required
def create_cover_letter_for_job(job_title):
    session['prefill_job_title'] = job_title
    return redirect(url_for('create_cover_letter'))

@app.route('/preview-resume-content/<int:resume_id>')
@login_required
def preview_resume_content(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    return render_template(f"resume_templates/{resume.template}.html", resume=resume)


@app.route('/payment')
@login_required
def payment():
    return render_template('payment.html')

@app.route('/generate-interview-qa', methods=['POST'])
@login_required
def generate_interview_qa_route():
    job_title = request.form.get('job_title')
    if not job_title:
        return redirect(url_for('interview_qa'))

    qa_content = generate_interview_qa(job_title)

    # Get or initialize the list
    interview_qa_list = session.get('interview_qa_list', [])
    interview_qa_list.append({'job_title': job_title, 'qa': qa_content})
    
    # Reassign the list back to session
    session['interview_qa_list'] = interview_qa_list

    # Ensure session is modified
    session.modified = True

    return redirect(url_for('interview_qa'))



@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    session['has_paid'] = True
    return redirect(url_for('dashboard'))

@app.route('/download-pdf/<int:resume_id>')
@login_required
def download_pdf(resume_id):
    if not session.get('has_paid'):
        return redirect(url_for('payment'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    rendered = render_template(f"resume_templates/{resume.template}.html", resume=resume)
    pdf = HTML(string=rendered).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={resume.title}.pdf'
    return response

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    resume_id = request.form.get('resume_id')
    plan = request.form.get('plan')
    
    # Handle subscription upgrade
    if plan:
        # Plan pricing (in cents for Stripe)
        plan_prices = {
            'Pro': 999,  # $9.99
            'Premium': 1999  # $19.99
        }
        
        if plan not in plan_prices:
            return redirect(url_for('my_account'))
        
        try:
            # In a real application, you would integrate with Stripe or another payment processor
            # For demo purposes, we'll simulate a successful payment
            
            # Simulate payment processing delay
            import time
            time.sleep(1)
            
            # Update user subscription
            current_user.subscription = plan
            db.session.commit()
            
            # Redirect back to account page with success message
            return redirect(url_for('my_account') + '?payment=success')
            
        except Exception as e:
            # Handle payment failure
            return redirect(url_for('my_account') + '?payment=failed')
    
    # Handle resume download payment
    if not resume_id:
        return "Missing resume_id", 400
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {'currency': 'usd', 'unit_amount': 499, 'product_data': {'name': 'Resume PDF Download'}},
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('download_pdf', resume_id=resume_id, _external=True),
            cancel_url=url_for('dashboard', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e), 400

@app.route('/resumes')
@login_required
def resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    return render_template('resumes.html', resumes=resumes, current_user=current_user, active_page='resumes')

@app.route('/cover_letters')
@login_required
def cover_letters():
    cover_letters = CoverLetter.query.filter_by(user_id=current_user.id).all()
    # Defensive: filter out any cover letters with missing, None, or invalid id
    valid_cover_letters = []
    for cl in cover_letters:
        if isinstance(getattr(cl, 'id', None), int) and getattr(cl, 'id', None) > 0:
            valid_cover_letters.append(cl)
        else:
            app.logger.warning(f"Skipping cover letter with invalid id: {getattr(cl, 'id', None)}")
    app.logger.info(f"Rendering cover_letters: {[cl.id for cl in valid_cover_letters]}")
    return render_template('cover_letters.html', cover_letters=valid_cover_letters, current_user=current_user, active_page='cover_letters')

@app.route('/interview_qa', methods=['GET', 'POST'])
@login_required
def interview_qa():
    interview_qa_list = session.get('interview_qa_list', [])
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        if job_title:
            qa_content = generate_interview_qa(job_title)
            interview_qa_list.append({'job_title': job_title, 'qa': qa_content})
            session['interview_qa_list'] = interview_qa_list
            session.modified = True
            return redirect(url_for('interview_qa'))
    return render_template('interview_qa.html', interview_qa_list=interview_qa_list, current_user=current_user, active_page='interview_qa')

def get_user_location():
    """Get user's approximate location using IP geolocation or return default."""
    try:
        # Try to get user's location from IP
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                city = data.get('city', '')
                region = data.get('regionName', '')
                country = data.get('country', '')
                if city and region:
                    return f"{city}, {region}"
                elif city:
                    return city
                elif region:
                    return region
    except:
        pass
    
    # Default to major US cities if location detection fails
    return "New York, NY"

@app.route('/jobs')
@login_required
def jobs():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    
    # If no location is specified, try to get user's location
    if not location:
        location = get_user_location()
    
    # If no keyword is specified, show general jobs
    if not keyword:
        keyword = 'software developer'  # Default search term for better results
    
    api_url = f'https://api.adzuna.com/v1/api/jobs/us/search/1'
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': keyword,
        'where': location,
        'results_per_page': 25,  # Show more jobs
        'content-type': 'application/json'
    }
    
    response = None
    error_message = None
    job_listings = []
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
    except requests.RequestException as e:
        print(f"Adzuna API error: {e}")
        error_message = 'Could not load jobs. Please try again later.'
    
    if response is not None:
        try:
            if response.status_code == 200:
                data = response.json()
                job_listings = [{
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', {}).get('display_name', 'N/A'),
                    'location': job.get('location', {}).get('display_name', 'N/A'),
                    'url': job.get('redirect_url', '#'),
                    'description': job.get('description', ''),
                    'salary': job.get('salary_min', None),
                    'salary_max': job.get('salary_max', None)
                } for job in data.get('results', [])]
            else:
                print(f"Adzuna API returned status {response.status_code}: {response.text}")
                error_message = 'Unable to fetch jobs at the moment. Please try again later.'
        except Exception as e:
            print(f"Error parsing Adzuna API response: {e}")
            error_message = 'Error processing job listings. Please try again later.'
    
    return render_template('jobs.html', 
                         jobs=job_listings, 
                         keyword=keyword, 
                         location=location, 
                         current_user=current_user, 
                         active_page='jobs', 
                         error_message=error_message)

@app.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    if request.method == 'POST':
        # Handle profile updates
        name = request.form.get('name')
        email = request.form.get('email')
        preferred_template = request.form.get('preferred_template')
        file = request.files.get('profile_pic')
        
        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Handle subscription changes
        change_subscription = request.form.get('change_subscription')
        subscription = request.form.get('subscription')
        
        # Handle account deletion
        delete_account = request.form.get('delete_account')
        
        if delete_account:
            # Delete all user data
            resumes = Resume.query.filter_by(user_id=current_user.id).all()
            for resume in resumes:
                db.session.delete(resume)
            
            cover_letters = CoverLetter.query.filter_by(user_id=current_user.id).all()
            for cover_letter in cover_letters:
                db.session.delete(cover_letter)
            
            # Delete user profile picture if exists
            if current_user.profile_pic:
                try:
                    profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_pic)
                    if os.path.exists(profile_pic_path):
                        os.remove(profile_pic_path)
                except:
                    pass
            
            # Delete the user account
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            return redirect(url_for('index'))
        
        if change_subscription and subscription:
            # Update subscription (this would integrate with payment processor in production)
            current_user.subscription = subscription
            db.session.commit()
            return redirect(url_for('my_account'))
        
        if current_password and new_password and confirm_password:
            # Verify current password
            if check_password_hash(current_user.password, current_password):
                if new_password == confirm_password:
                    if len(new_password) >= 6:
                        current_user.password = generate_password_hash(new_password)
                        db.session.commit()
                        return redirect(url_for('my_account'))
                    else:
                        return render_template('profile.html', user=current_user, active_page='my_account', 
                                             error="Password must be at least 6 characters long")
                else:
                    return render_template('profile.html', user=current_user, active_page='my_account', 
                                         error="New passwords do not match")
            else:
                return render_template('profile.html', user=current_user, active_page='my_account', 
                                     error="Current password is incorrect")
        
        # Handle profile information updates
        if name:
            current_user.name = name
        if email and email != current_user.email:
            # Check if email is already taken
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('profile.html', user=current_user, active_page='my_account', 
                                     error="Email already exists")
            current_user.email = email
        if preferred_template:
            current_user.preferred_template = preferred_template
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.profile_pic = filename
            
        db.session.commit()
        return redirect(url_for('my_account'))
    
    return render_template('profile.html', user=current_user, active_page='my_account')

def generate_resume_thumbnail(resume_id, html_content):
    """Generate a PNG thumbnail for the given resume HTML and save it to static/resume_thumbnails/{resume_id}.png"""
    from weasyprint import HTML
    import os
    # Render PDF to a temporary file
    pdf_path = f"/tmp/resume_{resume_id}.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    # Open PDF and render first page as PNG
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better quality
    out_dir = os.path.join('static', 'resume_thumbnails')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{resume_id}.png")
    pix.save(out_path)
    doc.close()
    os.remove(pdf_path)

@app.route('/analyze-resume/<int:resume_id>', methods=['GET'])
@login_required
def analyze_resume(resume_id):
    # Fetch the resume content (this assumes resumes are stored as text or can be converted to text)
    resume_path = os.path.join('static', 'resume_thumbnails', f'{resume_id}.png')
    if not os.path.exists(resume_path):
        return jsonify({'error': 'Resume not found'}), 404

    # Placeholder for ATS analysis logic
    # Replace this with actual analysis logic or API integration
    analysis_result = {
        'score': 85,  # Example score
        'recommendations': [
            'Use more keywords relevant to the job description.',
            'Avoid using tables or images for critical information.',
            'Ensure consistent formatting throughout the resume.'
        ]
    }

    return jsonify(analysis_result)

@app.route('/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['resume_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', 'resumes', filename)
        file.save(file_path)

        # Process the uploaded file (e.g., parse content, save to database, etc.)
        flash('Resume uploaded successfully!', 'success')
        return redirect(url_for('edit_resume', resume_id=1))  # Replace with actual resume ID

    flash('Invalid file type', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/edit-cover-letter/<int:letter_id>', methods=['GET', 'POST'])
@login_required
def edit_cover_letter(letter_id):
    # Fetch the cover letter by ID
    cover_letter = CoverLetter.query.get_or_404(letter_id)

    if request.method == 'POST':
        # Update the cover letter content
        cover_letter.content = request.form['content']
        db.session.commit()
        flash('Cover letter updated successfully!', 'success')
        return redirect(url_for('cover_letters'))

    return render_template('edit_cover_letter.html', cover_letter=cover_letter)

@app.route('/import-linkedin', methods=['GET', 'POST'])
@login_required
def import_linkedin():
    if request.method == 'POST':
        # Logic to handle LinkedIn data import
        flash('LinkedIn data imported successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('import_linkedin.html')

# Global error handler for BuildError
@app.errorhandler(BuildError)
def handle_build_error(e):
    return render_template('build_error.html', error_message=str(e)), 500

@app.route('/resume-creation-menu')
@login_required
def resume_creation_menu():
    return render_template('resume_creation_menu.html', current_user=current_user, active_page='resumes')

@app.route('/create-from-scratch')
@login_required
def create_from_scratch():
    return render_template('create_resume.html', current_user=current_user, active_page='resumes')

@app.route('/upload-existing-resume', methods=['GET', 'POST'])
@login_required
def upload_existing_resume():
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_existing_resume'))
        
        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_existing_resume'))
        
        if file and file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            try:
                # For now, create a basic resume entry and redirect to edit
                title = f"Uploaded Resume - {current_user.name or current_user.email}"
                content = "Please edit this resume with your information."
                template = 'classic'
                
                new_resume = Resume(user_id=current_user.id, title=title, content=content, template=template)
                db.session.add(new_resume)
                db.session.commit()
                
                # Generate basic thumbnail
                rendered_html = render_template(f"resume_templates/{template}.html", resume=new_resume)
                try:
                    generate_resume_thumbnail(new_resume.id, rendered_html)
                except Exception as e:
                    logging.error(f'Thumbnail generation failed: {e}')
                
                flash('Resume uploaded successfully! Please edit it with your information.', 'success')
                return redirect(url_for('edit_resume', resume_id=new_resume.id))
            except Exception as e:
                flash('Error processing uploaded file. Please try again.', 'danger')
                return redirect(url_for('upload_existing_resume'))
        else:
            flash('Please upload a PDF, DOC, or DOCX file.', 'danger')
    
    return render_template('upload_existing_resume.html', current_user=current_user, active_page='resumes')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting app on http://127.0.0.1:5003")
    app.run(debug=True, host='127.0.0.1', port=5003)
