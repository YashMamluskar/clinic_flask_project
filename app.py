from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from collections import defaultdict
# New imports for authentication
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
# http://127.0.0.1:5000/register_user to register new user
# In app.py

# ... (keep existing imports)
from functools import wraps # Add this new import

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = 'a-very-secret-key-that-is-long-and-secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'clinic.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app) # Initialize Bcrypt

# --- Flask-Login Configuration ---
login_manager = LoginManager(app)
login_manager.login_view = 'login' # The route to redirect to for login
login_manager.login_message_category = 'info' # Flash message category

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ---------------------------------

# --- Custom Decorator for Role-Based Access ---
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('patient_list'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# ---------------------------------------------


# --- Models ---
# The User model needs UserMixin for Flask-Login to work
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='reception') # e.g., 'reception', 'doctor', 'pharmacist'

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Patient(db.Model):
    # ... (Patient model remains the same)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    consultations = db.relationship('Consultation', backref='patient', lazy=True, cascade="all, delete-orphan")

class Consultation(db.Model):
    # ... (Consultation model remains the same)
    id = db.Column(db.Integer, primary_key=True)
    consultation_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    doctor_notes = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    prescriptions = db.relationship('Prescription', backref='consultation', lazy=True, cascade="all, delete-orphan")

class Prescription(db.Model):
    # ... (Prescription model remains the same)
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.id'), nullable=False)
# --------------


# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) # Changed to dashboard
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            # Redirect to dashboard after successful login
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    # After logging out, send the user back to the public home page
    return redirect(url_for('index'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register_user.html')
# -------------------------


# --- Protected Clinic Routes ---
@app.route('/')
def index():
    # If a user is already logged in, take them to the internal dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    # Otherwise, show the new public home page
    return render_template('home.html')

# In app.py, add this new route
@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_patients': Patient.query.count(),
        'total_consultations': Consultation.query.count(),
        'pending_prescriptions': Prescription.query.filter_by(status='Pending').count()
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/patients')
@login_required
def patient_list():
    # ... (function logic remains the same)
    query = request.args.get('search')
    if query:
        search_term = f"%{query}%"
        all_patients = Patient.query.filter(db.or_(Patient.name.ilike(search_term), Patient.email.ilike(search_term))).order_by(Patient.name).all()
    else:
        all_patients = Patient.query.order_by(Patient.name).all()
    return render_template('patient_list.html', patients=all_patients, search_query=query)

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register_patient():
    # ... (function logic remains the same)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone_number') or None
        existing_patient = Patient.query.filter_by(email=email).first()
        if existing_patient:
            flash('A patient with this email address already exists.', 'danger')
            return redirect(url_for('register_patient'))
        if phone:
            existing_phone = Patient.query.filter_by(phone_number=phone).first()
            if existing_phone:
                flash('A patient with this phone number already exists.', 'danger')
                return redirect(url_for('register_patient'))
        new_patient = Patient(name=name, email=email, phone_number=phone)
        db.session.add(new_patient)
        db.session.commit()
        flash(f'Patient {name} registered successfully!', 'success')
        return redirect(url_for('patient_list'))
    return render_template('register_patient.html')

# Add @login_required to the remaining routes
@app.route('/patient/<int:patient_id>')
@login_required
@role_required('doctor')
def patient_detail(patient_id):
    # ... (function logic remains the same)
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient_detail.html', patient=patient)

@app.route('/patient/<int:patient_id>/add_consultation', methods=['POST'])
@login_required
@role_required('doctor')
def add_consultation(patient_id):
    # ... (function logic remains the same)
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        diagnosis = request.form['diagnosis']
        notes = request.form['doctor_notes']
        new_consultation = Consultation(diagnosis=diagnosis, doctor_notes=notes, patient_id=patient.id)
        db.session.add(new_consultation)
        db.session.commit()
        flash('Consultation note saved successfully!', 'success')
    return redirect(url_for('patient_detail', patient_id=patient.id))

@app.route('/consultation/<int:consultation_id>/add_prescription', methods=['POST'])
@login_required
@role_required('doctor')
def add_prescription(consultation_id):
    # ... (function logic remains the same)
    consultation = Consultation.query.get_or_404(consultation_id)
    if request.method == 'POST':
        medicine_name = request.form['medicine_name']
        dosage = request.form['dosage']
        new_prescription = Prescription(medicine_name=medicine_name, dosage=dosage, consultation_id=consultation.id)
        db.session.add(new_prescription)
        db.session.commit()
        flash('Medication added to prescription.', 'success')
    return redirect(url_for('patient_detail', patient_id=consultation.patient_id))

@app.route('/pharmacy')
@login_required
@role_required('pharmacist')
def pharmacy_queue():
    # ... (function logic remains the same)
    pending_prescriptions = Prescription.query.filter_by(status='Pending').all()
    prescriptions_by_patient = defaultdict(list)
    for pres in pending_prescriptions:
        prescriptions_by_patient[pres.consultation.patient].append(pres)
    return render_template('pharmacy_queue.html', prescriptions_by_patient=prescriptions_by_patient)

@app.route('/dispense/<int:patient_id>', methods=['POST'])
@login_required
@role_required('pharmacist')
def dispense_meds(patient_id):
    # ... (function logic remains the same)
    pending_prescriptions = Prescription.query.join(Consultation).filter(Consultation.patient_id == patient_id, Prescription.status == 'Pending').all()
    for pres in pending_prescriptions:
        pres.status = 'Dispensed'
    db.session.commit()
    flash(f"All pending medications for patient dispensed.", 'success')
    return redirect(url_for('pharmacy_queue'))
# -------------------------
