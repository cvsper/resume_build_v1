from dotenv import load_dotenv
load_dotenv()

import os
import json
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response, jsonify, flash, send_from_directory
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

stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
if not stripe_publishable_key:
    raise RuntimeError("STRIPE_PUBLISHABLE_KEY environment variable not set. Please set it in your environment or Render dashboard.")

# Make Stripe publishable key available to all templates
@app.context_processor
def inject_stripe_key():
    return {'stripe_publishable_key': stripe_publishable_key}

supabase_db_url = os.getenv('SUPABASE_DB_URL')
if not supabase_db_url:
    raise RuntimeError('SUPABASE_DB_URL environment variable not set. Get your connection string from your Supabase project.')
app.config['SQLALCHEMY_DATABASE_URI'] = supabase_db_url
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Old SQLite, now disabled

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Configure session
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

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

# LinkedIn OAuth configuration
linkedin = oauth.register(
    name='linkedin',
    client_id=os.getenv('LINKEDIN_CLIENT_ID'),
    client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={'scope': 'r_liteprofile r_emailaddress'}
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
    stripe_customer_id = db.Column(db.String(100))  # Store Stripe customer ID
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

@app.route('/robots.txt')
def robots_txt():
    """Generate robots.txt for SEO"""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /preview-resume-content/
Disallow: /download-pdf/
Disallow: /delete-resume/
Disallow: /process-payment
Disallow: /create-checkout-session
Disallow: /upload-resume
Disallow: /logout

# Sitemap location
Sitemap: {sitemap_url}

# Crawl delay
Crawl-delay: 1""".format(sitemap_url=url_for('sitemap_xml', _external=True))
    
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/sitemap.xml')
def sitemap_xml():
    """Generate XML sitemap for SEO"""
    from datetime import datetime
    import xml.etree.ElementTree as ET
    
    # Create the root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Define public pages to include in sitemap
    pages = [
        {
            'url': url_for('index', _external=True),
            'changefreq': 'weekly',
            'priority': '1.0',
            'lastmod': '2024-01-15'
        },
        {
            'url': url_for('login', _external=True),
            'changefreq': 'monthly',
            'priority': '0.8',
            'lastmod': '2024-01-15'
        },
        {
            'url': url_for('register', _external=True),
            'changefreq': 'monthly',
            'priority': '0.8',
            'lastmod': '2024-01-15'
        }
    ]
    
    # Add each page to the sitemap
    for page in pages:
        url_element = ET.SubElement(urlset, 'url')
        
        loc = ET.SubElement(url_element, 'loc')
        loc.text = page['url']
        
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = page['lastmod']
        
        changefreq = ET.SubElement(url_element, 'changefreq')
        changefreq.text = page['changefreq']
        
        priority = ET.SubElement(url_element, 'priority')
        priority.text = page['priority']
    
    # Convert to string
    xml_str = ET.tostring(urlset, encoding='unicode')
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    
    response = make_response(xml_declaration + xml_str)
    response.headers['Content-Type'] = 'application/xml'
    return response

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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered! Please use a different email or login.', 'danger')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# OAuth Authentication Routes
@app.route('/auth/google')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/apple')
def apple_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Apple Sign In implementation would go here
    flash('Apple Sign In is coming soon!', 'info')
    return redirect(url_for('login'))

@app.route('/auth/linkedin')
def linkedin_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    redirect_uri = url_for('linkedin_callback', _external=True)
    return linkedin.authorize_redirect(redirect_uri)

@app.route('/callback/google')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
        
        if user_info:
            user = User.query.filter_by(email=user_info['email']).first()
            
            if not user:
                # Create new user
                user = User(
                    email=user_info['email'],
                    name=user_info.get('name', ''),
                    password=generate_password_hash('oauth_user'),  # Placeholder password
                    oauth_provider='google'
                )
                db.session.add(user)
                db.session.commit()
                flash('Account created successfully!', 'success')
            
            login_user(user)
            return redirect(url_for('dashboard'))
        
    except Exception as e:
        app.logger.error(f"Google OAuth error: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/callback/linkedin')
def linkedin_callback():
    try:
        token = linkedin.authorize_access_token()
        
        # Get user profile from LinkedIn
        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        
        # Get basic profile
        profile_response = requests.get(
            'https://api.linkedin.com/v2/people/~', 
            headers=headers
        )
        
        # Get email
        email_response = requests.get(
            'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
            headers=headers
        )
        
        if profile_response.status_code == 200 and email_response.status_code == 200:
            profile_data = profile_response.json()
            email_data = email_response.json()
            
            email = email_data['elements'][0]['handle~']['emailAddress']
            first_name = profile_data.get('localizedFirstName', '')
            last_name = profile_data.get('localizedLastName', '')
            full_name = f"{first_name} {last_name}".strip()
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                user = User(
                    email=email,
                    name=full_name,
                    password=generate_password_hash('oauth_user'),  # Placeholder password
                    oauth_provider='linkedin'
                )
                db.session.add(user)
                db.session.commit()
                flash('Account created successfully!', 'success')
            
            login_user(user)
            return redirect(url_for('dashboard'))
        
    except Exception as e:
        app.logger.error(f"LinkedIn OAuth error: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.name or user.email}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('index'))
    else:
        # User wasn't logged in, redirect silently without any message
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

@app.route('/pricing')
@login_required
def pricing():
    """Pricing page for subscription plan selection"""
    return render_template('pricing.html', current_user=current_user, active_page='pricing')


# Test route without authentication for pricing page UI testing
@app.route('/test-pricing-no-auth')
def test_pricing_no_auth():
    """Test pricing page template rendering without authentication requirement"""
    # Create mock user context
    from types import SimpleNamespace
    mock_user = SimpleNamespace()
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.profile_pic = None
    mock_user.subscription = "Free"
    
    return render_template('pricing.html', current_user=mock_user, active_page='pricing')


# Cover Letter Creation Route
@app.route('/create-cover-letter', methods=['GET', 'POST'])
@login_required
def create_cover_letter():
    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validation
        if not job_title:
            flash('Please enter a job title.', 'error')
            return render_template('create_cover_letter.html', current_user=current_user, active_page='cover_letters')
        
        if len(job_title) < 2:
            flash('Job title must be at least 2 characters long.', 'error')
            return render_template('create_cover_letter.html', current_user=current_user, active_page='cover_letters')
        
        name = current_user.name or current_user.email.split('@')[0].title()
        email = current_user.email
        
        try:
            # Use GPT to generate cover letter content
            content = generate_cover_letter(name, email, job_title, description)
            
            new_cover_letter = CoverLetter(
                user_id=current_user.id,
                job_title=job_title,
                content=content
            )
            db.session.add(new_cover_letter)
            db.session.commit()
            
            flash(f'Cover letter for "{job_title}" created successfully!', 'success')
            return redirect(url_for('cover_letters'))
            
        except Exception as e:
            app.logger.error(f"Error generating cover letter: {str(e)}")
            flash('Sorry, there was an error generating your cover letter. Please try again.', 'error')
            return render_template('create_cover_letter.html', current_user=current_user, active_page='cover_letters')
    
    return render_template('create_cover_letter.html', current_user=current_user, active_page='cover_letters')

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
        template = request.form.get('template', session.get('selected_template', 'classic'))
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

@app.route('/preview-resume-payment/<int:resume_id>')
@login_required
def preview_resume_payment(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    
    # Generate the PDF URL for preview
    pdf_url = url_for('preview_resume_content', resume_id=resume_id)
    
    return render_template('preview.html', 
                         resume_id=resume_id, 
                         pdf_url=pdf_url, 
                         resume=resume)

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

@app.route('/payment-success/<int:resume_id>')
@login_required
def payment_success(resume_id):
    # Mark payment as completed
    session['has_paid'] = True
    # Redirect to actual PDF download
    return redirect(url_for('download_pdf', resume_id=resume_id))

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Enhanced webhook signature verification for production security
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        if webhook_secret:
            # Production mode - verify signature
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            print(f"✅ Webhook signature verified for event: {event.get('type', 'unknown')}")
        else:
            # Development mode - parse payload without verification
            import json
            event = json.loads(payload)
            print(f"⚠️  Development mode: Processing webhook without signature verification")
        
        # Enhanced logging
        event_type = event.get('type', 'unknown')
        event_id = event.get('id', 'unknown')
        print(f"📨 Processing webhook: {event_type} (ID: {event_id})")
        
        # Handle different webhook events
        if event.get('type') == 'checkout.session.completed':
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid checkout.session.completed event structure")
                return '', 200
                
            session_data = event['data']['object']
            session_id = session_data.get('id', 'unknown')
            
            # Check if it's a subscription or one-time payment
            if session_data.get('mode') == 'subscription':
                # Handle subscription payment
                user_id = session_data.get('metadata', {}).get('user_id')
                plan = session_data.get('metadata', {}).get('plan')
                customer_id = session_data.get('customer')
                
                if user_id and plan:
                    # Update user subscription in database
                    user = User.query.get(user_id)
                    if user:
                        # Update both subscription and Stripe customer ID
                        user.subscription = plan
                        if customer_id and not user.stripe_customer_id:
                            user.stripe_customer_id = customer_id
                        db.session.commit()
                        print(f"✅ Subscription activated: User {user.email} → {plan} (Customer: {customer_id})")
                    else:
                        print(f"⚠️  User not found for subscription: {user_id}")
                else:
                    print(f"⚠️  Missing metadata in subscription session: {session_id}")
            else:
                # Handle one-time payment (resume downloads)
                print(f"✅ One-time payment successful for session: {session_id}")
            
            # Log payment details
            amount = session_data.get('amount_total', 0) / 100  # Convert from cents
            currency = session_data.get('currency', 'usd').upper()
            print(f"   Amount: {currency} ${amount:.2f}")
            
        elif event.get('type') == 'invoice.payment_succeeded':
            # Handle successful recurring subscription payments
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid invoice.payment_succeeded event structure")
                return '', 200
                
            invoice = event['data']['object']
            customer_id = invoice.get('customer')
            subscription_id = invoice.get('subscription')
            amount = invoice.get('amount_paid', 0) / 100
            currency = invoice.get('currency', 'usd').upper()
            print(f"✅ Recurring payment successful: {subscription_id}")
            print(f"   Customer: {customer_id}, Amount: {currency} ${amount:.2f}")
            
        elif event.get('type') == 'invoice.payment_failed':
            # Handle failed subscription payments
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid invoice.payment_failed event structure")
                return '', 200
                
            invoice = event['data']['object']
            customer_id = invoice.get('customer')
            subscription_id = invoice.get('subscription')
            attempt_count = invoice.get('attempt_count', 1)
            print(f"❌ Recurring payment failed: {subscription_id}")
            print(f"   Customer: {customer_id}, Attempt: {attempt_count}")
            
            # Find user and potentially update subscription status
            if customer_id:
                user = User.query.filter_by(stripe_customer_id=customer_id).first()
                if user:
                    print(f"   Associated user: {user.email}")
                    # Note: Don't immediately downgrade - Stripe handles retries
            
        elif event.get('type') == 'customer.subscription.deleted':
            # Handle subscription cancellation
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid customer.subscription.deleted event structure")
                return '', 200
                
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            subscription_id = subscription.get('id')
            print(f"🔄 Subscription cancelled: {subscription_id}")
            
            # Find user and downgrade to Free plan
            if customer_id:
                user = User.query.filter_by(stripe_customer_id=customer_id).first()
                if user:
                    user.subscription = 'Free'
                    db.session.commit()
                    print(f"   User {user.email} downgraded to Free plan")
            
        elif event.get('type') == 'customer.subscription.updated':
            # Handle subscription updates (plan changes, etc.)
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid customer.subscription.updated event structure")
                return '', 200
                
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            status = subscription.get('status')
            print(f"🔄 Subscription updated: {subscription.get('id')} → Status: {status}")
            
        elif event.get('type') == 'payment_intent.succeeded':
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid payment_intent.succeeded event structure")
                return '', 200
                
            payment_intent = event['data']['object']
            amount = payment_intent.get('amount', 0) / 100
            currency = payment_intent.get('currency', 'usd').upper()
            print(f"✅ Payment intent succeeded: {payment_intent['id']}")
            print(f"   Amount: {currency} ${amount:.2f}")
            
        elif event.get('type') == 'payment_intent.payment_failed':
            if 'data' not in event or 'object' not in event['data']:
                print("⚠️  Invalid payment_intent.payment_failed event structure")
                return '', 200
                
            payment_intent = event['data']['object']
            failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown')
            print(f"❌ Payment failed: {payment_intent['id']}")
            print(f"   Reason: {failure_reason}")
            
        else:
            print(f"📋 Unhandled webhook event: {event.get('type', 'unknown')}")
            
        return '', 200
        
    except stripe.error.SignatureVerificationError as e:
        print(f"🚨 Webhook signature verification failed: {e}")
        print(f"   Payload length: {len(payload)}")
        print(f"   Signature header: {sig_header[:50] if sig_header else 'None'}...")
        return 'Invalid signature', 400
        
    except json.JSONDecodeError as e:
        print(f"🚨 Invalid JSON payload: {e}")
        return 'Invalid JSON', 400
        
    except Exception as e:
        print(f"🚨 Webhook processing error: {e}")
        import traceback
        traceback.print_exc()
        return 'Webhook error', 500

@app.route('/download-pdf/<int:resume_id>')
@login_required
def download_pdf(resume_id):
    if not session.get('has_paid'):
        return redirect(url_for('preview_resume_payment', resume_id=resume_id))
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
    try:
        # Log request data for debugging
        print(f"POST data: {request.form}")
        print(f"Headers: {dict(request.headers)}")
        
        resume_id = request.form.get('resume_id')
        plan = request.form.get('plan')
        
        print(f"Received resume_id: {resume_id}, plan: {plan}")
        
        # Handle subscription upgrade
        if plan:
            # Plan pricing (in cents for Stripe)
            plan_prices = {
                'Pro': 999,  # $9.99
                'Premium': 1999  # $19.99
            }
            
            if plan not in plan_prices:
                print(f"Invalid plan: {plan}")
                return redirect(url_for('my_account'))
            
            try:
                # Create Stripe Checkout Session for subscription
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': plan_prices[plan],
                            'product_data': {
                                'name': f'{plan} Subscription',
                                'description': f'Monthly {plan} subscription with unlimited features'
                            },
                            'recurring': {
                                'interval': 'month'
                            }
                        },
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url=url_for('subscription_success', plan=plan, _external=True),
                    cancel_url=url_for('my_account', _external=True),
                    customer_email=current_user.email,
                    metadata={
                        'user_id': current_user.id,
                        'plan': plan
                    }
                )
                print(f"Subscription checkout session created: {checkout_session.id}")
                return redirect(checkout_session.url, code=303)
                
            except Exception as e:
                print(f"Stripe subscription error: {e}")
                return redirect(url_for('my_account') + '?payment=failed')
        
        # Handle resume download payment
        if not resume_id:
            print("Missing resume_id in request")
            return "Missing resume_id", 400
            
        # Validate resume_id and ownership
        try:
            resume = Resume.query.get(resume_id)
            if not resume:
                print(f"Resume not found: {resume_id}")
                return "Resume not found", 404
                
            if resume.user_id != current_user.id:
                print(f"Unauthorized access to resume {resume_id} by user {current_user.id}")
                return "Unauthorized", 403
        except Exception as e:
            print(f"Database error checking resume: {e}")
            return "Database error", 500
        
        try:
            print(f"Creating checkout session for resume {resume_id}")
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd', 
                        'unit_amount': 499, 
                        'product_data': {
                            'name': 'Resume PDF Download',
                            'description': f'Download for Resume #{resume_id}'
                        }
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('payment_success', resume_id=resume_id, _external=True),
                cancel_url=url_for('preview_resume_payment', resume_id=resume_id, _external=True),
                metadata={
                    'user_id': current_user.id,
                    'resume_id': resume_id,
                    'type': 'resume_download'
                }
            )
            print(f"Resume checkout session created: {checkout_session.id}")
            return redirect(checkout_session.url, code=303)
            
        except Exception as e:
            print(f"Stripe resume payment error: {e}")
            return f"Payment error: {str(e)}", 400
            
    except Exception as e:
        print(f"Unexpected error in create_checkout_session: {e}")
        return f"Server error: {str(e)}", 500

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
    # Handle success messages from URL parameters
    success_message = None
    error_message = None
    
    payment_status = request.args.get('payment')
    plan = request.args.get('plan')
    change_type = request.args.get('type')
    
    if payment_status == 'success' and plan:
        if change_type == 'upgrade':
            success_message = f"🎉 Welcome to {plan}! Your subscription has been successfully activated."
        elif change_type == 'change':
            success_message = f"✅ Your subscription has been changed to {plan}."
        elif change_type == 'reactivate':
            success_message = f"🔄 Your {plan} subscription has been reactivated."
        else:
            success_message = f"✅ Subscription updated to {plan} plan."
    elif payment_status == 'failed':
        error_message = "❌ Payment failed. Please try again or contact support."
    
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
                                             error="Password must be at least 6 characters long",
                                             success_message=success_message)
                else:
                    return render_template('profile.html', user=current_user, active_page='my_account', 
                                         error="New passwords do not match",
                                         success_message=success_message)
            else:
                return render_template('profile.html', user=current_user, active_page='my_account', 
                                     error="Current password is incorrect",
                                     success_message=success_message)
        
        # Handle profile information updates
        if name:
            current_user.name = name
        if email and email != current_user.email:
            # Check if email is already taken
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('profile.html', user=current_user, active_page='my_account', 
                                     error="Email already exists",
                                     success_message=success_message)
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
    
    return render_template('profile.html', 
                         user=current_user, 
                         active_page='my_account',
                         success_message=success_message,
                         error_message=error_message)

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
    logging.info(f"Upload route accessed by user: {current_user.email if current_user.is_authenticated else 'Anonymous'}")
    
    if request.method == 'POST':
        logging.info("POST request received for file upload")
        
        if 'resume_file' not in request.files:
            logging.warning("No file in request")
            flash('No file selected', 'danger')
            return redirect(url_for('upload_existing_resume'))
        
        file = request.files['resume_file']
        logging.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logging.warning("Empty filename")
            flash('No file selected', 'danger')
            return redirect(url_for('upload_existing_resume'))
        
        if file and file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            try:
                logging.info(f"Processing file: {file.filename}")
                # Import the file parser
                from resume.file_parser import parse_resume_file
                
                # Parse the uploaded file
                logging.info(f"Parsing uploaded file: {file.filename}")
                parsed_data = parse_resume_file(file, file.filename)
                logging.info(f"Parsing completed. Title: {parsed_data['title']}, Content length: {len(parsed_data['content'])}")
                
                # Create resume with parsed content
                title = parsed_data['title']
                content = parsed_data['content']
                template = current_user.preferred_template or 'classic'
                
                new_resume = Resume(user_id=current_user.id, title=title, content=content, template=template)
                db.session.add(new_resume)
                db.session.commit()
                logging.info(f"Resume created with ID: {new_resume.id}")
                
                # Generate thumbnail
                rendered_html = render_template(f"resume_templates/{template}.html", resume=new_resume)
                try:
                    generate_resume_thumbnail(new_resume.id, rendered_html)
                    logging.info("Thumbnail generated successfully")
                except Exception as e:
                    logging.error(f'Thumbnail generation failed: {e}')
                
                # Provide appropriate feedback based on parsing success
                if parsed_data['raw_text'] and len(parsed_data['raw_text']) > 50:
                    flash(f'Resume uploaded and parsed successfully! We extracted {len(parsed_data["sections"])} sections. Please review and edit as needed.', 'success')
                    logging.info("Success message set for good parsing")
                else:
                    flash('Resume uploaded! We were unable to extract text content automatically. Please add your resume content in the editor.', 'warning')
                    logging.info("Warning message set for poor parsing")
                
                logging.info(f"Redirecting to edit_resume with resume_id: {new_resume.id}")
                return redirect(url_for('edit_resume', resume_id=new_resume.id))
                
            except Exception as e:
                logging.error(f'Error processing uploaded file: {e}')
                import traceback
                logging.error(f'Full traceback: {traceback.format_exc()}')
                flash('Error processing uploaded file. The file may be corrupted or in an unsupported format. Please try again or create a new resume.', 'danger')
                return redirect(url_for('upload_existing_resume'))
        else:
            logging.warning(f"Invalid file type: {file.filename}")
            flash('Please upload a PDF, DOC, or DOCX file.', 'danger')
    
    logging.info("Rendering upload template")
    return render_template('upload_existing_resume.html', current_user=current_user, active_page='resumes')

@app.route('/clear-prefill-job-title', methods=['POST'])
@login_required
def clear_prefill_job_title():
    session.pop('prefill_job_title', None)
    return jsonify({'success': True})

# API Routes for Stripe Configuration
@app.route('/api/stripe-config')
def get_stripe_config():
    """Provide Stripe publishable key for frontend"""
    return jsonify({'publishable_key': stripe_publishable_key})

@app.route('/choose-design', methods=['GET', 'POST'])
@login_required
def choose_design():
    if request.method == 'POST':
        template = request.form.get('template', 'classic')
        # Store selected template in session for the resume creation process
        session['selected_template'] = template
        return redirect(url_for('create_resume'))
    return render_template('choose_design.html')

@app.route('/preview-template/<template_name>')
@login_required
def preview_template(template_name):
    # Validate template name
    valid_templates = ['classic', 'modern', 'elegant', 'minimal', 'professional', 'executive', 'creative']
    if template_name not in valid_templates:
        return "Invalid template", 404
    
    # Create a sample resume object for preview
    sample_resume = type('obj', (object,), {
        'title': 'Sample Resume',
        'content': '''
        <h2>John Doe</h2>
        <p>Email: john.doe@email.com | Phone: (555) 123-4567</p>
        
        <h3>Experience</h3>
        <div>
            <strong>Software Engineer</strong> - Tech Company (2020-Present)
            <ul>
                <li>Developed web applications using modern frameworks</li>
                <li>Collaborated with cross-functional teams</li>
                <li>Improved system performance by 30%</li>
            </ul>
        </div>
        
        <h3>Education</h3>
        <div>
            <strong>Bachelor of Science in Computer Science</strong><br>
            University Name (2016-2020)
        </div>
        
        <h3>Skills</h3>
        <p>Python, JavaScript, React, SQL, Git</p>
        '''
    })
    
    return render_template(f"resume_templates/{template_name}.html", resume=sample_resume)

@app.route('/subscription-success/<plan>')
@login_required
def subscription_success(plan):
    """Handle successful subscription payments"""
    try:
        # Update user subscription in database
        if plan in ['Pro', 'Premium']:
            old_plan = current_user.subscription or 'Free'
            current_user.subscription = plan
            db.session.commit()
            
            # Log successful subscription
            print(f"✅ User {current_user.email} successfully changed subscription: {old_plan} → {plan}")
            
            # Determine success message based on change type
            if old_plan == 'Free':
                message_type = 'upgrade'
            elif old_plan != plan:
                message_type = 'change'
            else:
                message_type = 'reactivate'
            
            # Redirect to account page with success message
            return redirect(url_for('my_account') + f'?payment=success&plan={plan}&type={message_type}')
        else:
            print(f"❌ Invalid plan in subscription success: {plan}")
            return redirect(url_for('my_account') + '?payment=failed')
            
    except Exception as e:
        print(f"Error in subscription success handler: {e}")
        return redirect(url_for('my_account') + '?payment=failed')

# Add new Stripe webhook endpoints and enhanced subscription management
@app.route('/create-customer-portal', methods=['POST'])
@login_required
def create_customer_portal():
    """Create a Stripe Customer Portal session for subscription management"""
    print("=== CUSTOMER PORTAL REQUEST RECEIVED ===")
    print(f"Request method: {request.method}")
    print(f"Request form data: {request.form}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"User: {current_user.email}")
    print("==========================================")
    
    try:
        # Get or create Stripe customer for the user
        customer_id = current_user.stripe_customer_id
        print(f"Current customer_id: {customer_id}")
        
        if not customer_id:
            print("Creating new Stripe customer...")
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name or current_user.email.split('@')[0],
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
            customer_id = customer.id
            print(f"Created new customer: {customer_id}")
        
        print("Creating Customer Portal session...")
        # Create Customer Portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=url_for('dashboard', _external=True)
        )
        
        print(f"Portal session created: {portal_session.url}")
        print("Redirecting to Stripe Customer Portal...")
        return redirect(portal_session.url, code=303)
        
    except Exception as e:
        print(f"Customer Portal error: {e}")
        flash('Unable to access billing portal. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/subscription-billing-history')
@login_required
def subscription_billing_history():
    """Get user's billing history from Stripe"""
    try:
        if not current_user.stripe_customer_id:
            return jsonify({'invoices': []})
        
        # Get customer's invoices
        invoices = stripe.Invoice.list(
            customer=current_user.stripe_customer_id,
            limit=20
        )
        
        billing_history = []
        for invoice in invoices.data:
            billing_history.append({
                'id': invoice.id,
                'amount': invoice.amount_paid / 100,  # Convert from cents
                'currency': invoice.currency.upper(),
                'status': invoice.status,
                'created': datetime.fromtimestamp(invoice.created).strftime('%Y-%m-%d'),
                'description': invoice.description or 'Subscription payment',
                'invoice_pdf': invoice.invoice_pdf,
                'hosted_invoice_url': invoice.hosted_invoice_url
            })
        
        return jsonify({'invoices': billing_history})
        
    except Exception as e:
        print(f"Billing history error: {e}")
        return jsonify({'error': 'Unable to retrieve billing history'})

@app.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user's active subscription"""
    try:
        if not current_user.stripe_customer_id:
            flash('No active subscription found.', 'error')
            return redirect(url_for('my_account'))
        
        # Get customer's active subscriptions
        subscriptions = stripe.Subscription.list(
            customer=current_user.stripe_customer_id,
            status='active'
        )
        
        if subscriptions.data:
            # Cancel the first active subscription
            subscription = subscriptions.data[0]
            stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=True
            )
            
            flash('Your subscription will be cancelled at the end of the current billing period.', 'success')
        else:
            flash('No active subscription found to cancel.', 'error')
        
        return redirect(url_for('my_account'))
        
    except Exception as e:
        print(f"Subscription cancellation error: {e}")
        flash('Unable to cancel subscription. Please try again.', 'error')
        return redirect(url_for('my_account'))

@app.route('/reactivate-subscription', methods=['POST'])
@login_required
def reactivate_subscription():
    """Reactivate a cancelled subscription"""
    try:
        if not current_user.stripe_customer_id:
            flash('No subscription found.', 'error')
            return redirect(url_for('my_account'))
        
        # Get customer's subscriptions
        subscriptions = stripe.Subscription.list(
            customer=current_user.stripe_customer_id,
            status='all'
        )
        
        for subscription in subscriptions.data:
            if subscription.cancel_at_period_end:
                # Reactivate subscription
                stripe.Subscription.modify(
                    subscription.id,
                    cancel_at_period_end=False
                )
                flash('Your subscription has been reactivated!', 'success')
                return redirect(url_for('my_account'))
        
        flash('No cancelled subscription found to reactivate.', 'error')
        return redirect(url_for('my_account'))
        
    except Exception as e:
        print(f"Subscription reactivation error: {e}")
        flash('Unable to reactivate subscription. Please try again.', 'error')
        return redirect(url_for('my_account'))

@app.route('/downgrade-subscription', methods=['POST'])
@login_required
def downgrade_subscription():
    """Handle subscription downgrades and cancellations"""
    try:
        plan = request.form.get('plan', '').strip()
        print(f"Downgrade request: User {current_user.email} -> {plan}")
        
        if plan == 'Free':
            # Cancel subscription and downgrade to free
            if current_user.stripe_customer_id:
                try:
                    # Get active subscriptions
                    subscriptions = stripe.Subscription.list(
                        customer=current_user.stripe_customer_id,
                        status='active'
                    )
                    
                    # Cancel all active subscriptions
                    for subscription in subscriptions.data:
                        stripe.Subscription.modify(
                            subscription.id,
                            cancel_at_period_end=True
                        )
                        print(f"Scheduled cancellation for subscription: {subscription.id}")
                    
                    # Update user in database
                    current_user.subscription = 'Free'
                    db.session.commit()
                    
                    flash('Your subscription will be cancelled at the end of the current billing period. You will then be on the Free plan.', 'success')
                    
                except stripe.error.StripeError as e:
                    print(f"Stripe error during cancellation: {e}")
                    flash('Unable to cancel subscription. Please try again or contact support.', 'error')
                    
            else:
                # User already on free plan
                current_user.subscription = 'Free'
                db.session.commit()
                flash('You are now on the Free plan.', 'info')
                
        elif plan in ['Pro', 'Premium']:
            # Handle plan changes (upgrade/downgrade between paid plans)
            if current_user.stripe_customer_id:
                try:
                    # Create new checkout session for plan change
                    plan_prices = {
                        'Pro': 999,      # $9.99
                        'Premium': 1999  # $19.99
                    }
                    
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': plan_prices[plan],
                                'product_data': {
                                    'name': f'{plan} Subscription',
                                    'description': f'Monthly {plan} subscription with unlimited features'
                                },
                                'recurring': {
                                    'interval': 'month'
                                }
                            },
                            'quantity': 1,
                        }],
                        mode='subscription',
                        customer=current_user.stripe_customer_id,
                        success_url=url_for('subscription_success', plan=plan, _external=True),
                        cancel_url=url_for('my_account', _external=True),
                        metadata={
                            'user_id': current_user.id,
                            'plan': plan,
                            'change_type': 'plan_change'
                        }
                    )
                    
                    return redirect(checkout_session.url, code=303)
                    
                except stripe.error.StripeError as e:
                    print(f"Stripe error during plan change: {e}")
                    flash('Unable to change plan. Please try again.', 'error')
                    
            else:
                # Redirect to regular upgrade flow
                return redirect(url_for('create_checkout_session') + f'?plan={plan}')
        else:
            flash('Invalid plan selected.', 'error')
            
        return redirect(url_for('my_account'))
        
    except Exception as e:
        print(f"Downgrade subscription error: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('my_account'))

@app.route('/debug-subscription')
def debug_subscription():
    """Debug page for testing subscription button flow"""
    return send_from_directory('.', 'debug_subscription_flow.html')

@app.route('/debug-subscription-detailed')
def debug_subscription_detailed():
    """Serve the detailed debug page for subscription testing"""
    return send_from_directory('.', 'debug_subscription_detailed.html')

@app.route('/test-subscription-button')
def test_subscription_button():
    """Simple test page for subscription button"""
    return send_from_directory('.', 'test_subscription_button.html')

@app.route('/test-subscription-simple')
def test_subscription_simple():
    """Serve the simple subscription test page"""
    return send_from_directory('.', 'test_subscription_simple.html')

# Test route without authentication for subscription button testing
@app.route('/test-dashboard-no-auth')
def test_dashboard_no_auth():
    """Test dashboard template rendering without authentication requirement"""
    # Create mock data for testing
    mock_resumes = []
    mock_cover_letters = []
    mock_interview_qa_list = []
    
    # Create mock user context
    from types import SimpleNamespace
    mock_user = SimpleNamespace()
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.profile_pic = None
    mock_user.subscription = "Free"
    
    return render_template('dashboard.html', 
                           resumes=mock_resumes, 
                           cover_letters=mock_cover_letters, 
                           interview_qa_list=mock_interview_qa_list,
                           current_user=mock_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting app on http://127.0.0.1:5009")
    app.run(debug=True, host='127.0.0.1', port=5009)
