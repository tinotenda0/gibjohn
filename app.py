from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import User
app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        return db.query(User).get(int(user_id))
    finally:
        db.close()


@app.before_request
def create_tables():
    from models import Base
    Base.metadata.create_all(bind=engine)
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/logout')
def logout():
    logout_user()
    flash ('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        db = SessionLocal()
        try:
            user = db.query(User).filter_by(email=email).first()
            if user:
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))

            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(email=email, name=name, password_hash=password_hash)
            db.add(new_user)
            db.commit()

            flash('Registration successful', 'success')
            return redirect(url_for('login'))
        finally:
            db.close()
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
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

login_manager.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)