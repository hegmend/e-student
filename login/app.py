from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth.html', is_signup=False, page_title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not first_name or not last_name:
            flash('Будь ласка, вкажіть імʼя та прізвище', 'error')
            return render_template('auth.html', is_signup=True, page_title='Register')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth.html', is_signup=True, page_title='Register')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth.html', is_signup=True, page_title='Register')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('auth.html', is_signup=True, page_title='Register')
        
        try:
            new_user = User(
                email=email.strip(),
                first_name=first_name,
                last_name=last_name
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Перевірка, що користувач зберігся
            saved_user = User.query.filter_by(email=email.strip()).first()
            if saved_user:
                print(f"Користувач успішно збережений: {saved_user.email} (ID: {saved_user.id})")
            else:
                print("ПОМИЛКА: Користувач не знайдений після збереження!")
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Помилка при реєстрації: {str(e)}', 'error')
            print(f"Помилка реєстрації: {e}")  # Для діагностики в консолі
            return render_template('auth.html', is_signup=True, page_title='Register')
    
    return render_template('auth.html', is_signup=True, page_title='Register')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', email=user.email, user=user)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# Initialize database
with app.app_context():
    db.create_all()
    # Перевірка шляху до бази даних
    db_path = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"База даних знаходиться за адресою: {db_path}")
    if 'instance' in db_path or not os.path.isabs(db_path.split('///')[-1] if '///' in db_path else db_path):
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        db_file = os.path.join(instance_path, 'users.db')
        print(f"Повний шлях до бази даних: {os.path.abspath(db_file)}")

if __name__ == '__main__':
    app.run(debug=True)