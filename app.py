#importing libraries

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()




#importing database models
from models import User, Course, Enrollment, Roles

# Configuring flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("POSTGRES_URL").replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY", 'cb0aab5c73d0a14b3d74b62a407b8539beb10ffe480389d0a70f746cea0b7bda')


#Database connection
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

# Initialising extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Creating the user loader function
@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        return db.query(User).get(int(user_id))
    finally:
        db.close()

# Creating database tables
@app.before_request
def create_tables():
    from models import Base
    Base.metadata.create_all(bind=engine)

#Defining the base route
@app.route('/')
def index():
    return render_template('index.html')

#Defining error pages
#404
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

#500
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

#Defining authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Getting html form data
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name').capitalize()
        password = request.form.get('password')
        role = request.form.get('role', 'student').lower()

        # Querying the database to check if the user already exists by their email
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(email=email).first()
            if user:
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))

            # Hashing the password and creating a new user object
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            role_enum = Roles.tutor if role == 'tutor' else Roles.student
            new_user = User(email=email, name=name, password_hash=password_hash , role=role_enum)
            db.add(new_user)
            db.commit()

            flash('Registration successful', 'success')
            return redirect(url_for('login'))
        finally:
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Getting html form data
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Querying the database to verify user credentials and logging them in if successful
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user, remember=remember)
                return redirect(url_for('dashboard'))
            flash('Please check your login details and try again.', 'danger')
        finally:
            db.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Logout user and redirect to the login page
    logout_user()
    flash ('You have been logged out', 'success')
    return redirect(url_for('login'))

# Creating routes for course management
def courses():
    db = SessionLocal()
    try:
        return db.query(Course).all()
    finally:
        db.close()

@app.route('/courses')
@login_required
def course_list():
    all_courses = courses()
    return render_template('courses.html', courses=all_courses)

# Creating single course view
@app.route('/courses/<int:course_id>')
@login_required
def course_detail(course_id):
    db = SessionLocal()
    # Querying the database for the course with the given id
    try:
        course = db.query(Course).get(course_id)
        if not course:
            flash('Course not found', 'danger')
            return redirect(url_for('course_list'))
        return render_template('course_detail.html', course=course)
    finally:
        db.close()

# Initialising course edit and new course routes
@app.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    # Restricting course editing to tutors only
    if current_user.role.value != 'tutor':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('dashboard'))
    else:
        db = SessionLocal()
        try:
            course = db.query(Course).get(course_id)
            if not course:
                flash('Course not found', 'danger')
                return redirect(url_for('course_list'))
            return render_template('edit_course.html', course=course)
        finally:
            db.close()

@app.route('/courses/new', methods=['GET', 'POST'])
@login_required
def new_course():
    # Restricting course creation to tutors only
    if current_user.role.value != 'tutor':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('dashboard'))
    else:
        if request.method == 'POST':
            title = request.form.get('title')
            category = request.form.get('category')

            db = SessionLocal()
            try:
                new_course = Course(title=title, category=category)
                db.add(new_course)
                db.commit()

                flash('New course added successfully', 'success')
                return redirect(url_for('dashboard'))
            finally:
                db.close()
        return render_template('new_course.html')

# Setting up student enrollment routes
@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    # Restricting enrollment to students only
    if current_user.role != 'user':
        flash('Only students can enroll in courses', 'danger')
        return redirect(url_for('dashboard'))
    else:
        db = SessionLocal()
        # Querying the database for the course with the given id and checking if the user is already enrolled
        try:
            enrollment = db.query(Enrollment).filter_by(user_id=current_user.id, course_id=course_id).first()
            if enrollment:
                flash('You are already enrolled in this course', 'info')
                return redirect(url_for('dashboard'))

            new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
            db.add(new_enrollment)
            db.commit()

            flash('Enrolled in course successfully', 'success')
            return redirect(url_for('dashboard'))
        finally:
            db.close()

# User dashboard setup
@app.route('/dashboard')
@login_required
def dashboard():
    def all_users():
        db = SessionLocal()
        try:
            return db.query(User).all()
        finally:
            db.close()
    return render_template('dashboard.html', users=all_users())

# User profile page setup
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Getting html form data and applying changes to the user profile
    if request.method == 'POST':
        name = request.form.get('name')

        db = SessionLocal()
        try:
            user = db.query(User).get(current_user.id)
            user.name = name
            db.commit()
            flash('Profile updated successfully', 'success')
        finally:
            db.close()
    return render_template('profile.html')

@app.route('/feedback')
def feedback ():
    return render_template('feedback.html')

login_manager.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)