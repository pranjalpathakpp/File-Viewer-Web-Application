from flask import Flask, render_template, redirect, url_for, flash, send_from_directory, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Pranjal Pathak/Desktop/Web development/myflaskapp/instance/database.db'
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=8, max=80)])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_exists(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return os.path.isfile(file_path)    

def file_exists_in_trash(filename):
    trash_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'trash')
    file_path = os.path.join(trash_folder, filename)
    return os.path.isfile(file_path)

@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_file = File(filename=filename, owner_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()

    # Only retrieve files that haven't been deleted.
    files = File.query.filter_by(owner_id=current_user.id, is_deleted=False).all()

    return render_template('dashboard.html', files=files, title='Dashboard', file_exists=file_exists)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        print("Login form data: ", login_form.data) 
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    else:
        print("Login form did not validate. Errors: ", login_form.errors) 

    return render_template('index.html', login_form=login_form, signup_form=RegisterForm())

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    signup_form = RegisterForm()

    if signup_form.validate_on_submit():
        print("Signup form data: ", signup_form.data) 
        hashed_password = generate_password_hash(signup_form.password.data, method='sha256')
        new_user = User(email=signup_form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        print("Signup form did not validate. Errors: ", signup_form.errors)

    return render_template('index.html', login_form=LoginForm(), signup_form=signup_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/recents')
@login_required
def recents():
    # Only retrieve recent files that haven't been deleted.
    recent_files = File.query.filter_by(owner_id=current_user.id, is_deleted=False).order_by(File.uploaded_at.desc()).limit(10).all()
    return render_template('dashboard.html', files=recent_files, title='Recents', file_exists=file_exists)


@app.route('/synced')
@login_required
def synced():
    # Only retrieve synced files that haven't been deleted.
    synced_files = File.query.filter_by(owner_id=current_user.id, is_deleted=False).all()
    return render_template('dashboard.html', files=synced_files, title='Synced', file_exists=file_exists)


@app.route('/trash', methods=['GET', 'POST'])
@login_required
def trash():
    if request.method == 'POST':
        # Delete all files in the trash for the current user
        trashed_files = File.query.filter_by(owner_id=current_user.id, is_deleted=True).all()

        for file in trashed_files:
            # Delete the file from the file system
            trash_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'trash')
            file_path = os.path.join(trash_folder, file.filename)
            os.remove(file_path)

        # Delete all trashed files from the database
        File.query.filter_by(owner_id=current_user.id, is_deleted=True).delete()
        db.session.commit()

        return jsonify({"success": True}), 200

    # Only retrieve trashed files that have been deleted.
    trashed_files = File.query.filter_by(owner_id=current_user.id, is_deleted=True).order_by(File.updated_at.desc()).all()
    return render_template('dashboard.html', files=trashed_files, title='Trash', file_exists_in_trash=file_exists_in_trash)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_file = File(filename=filename, owner_id=current_user.id)
        db.session.add(new_file)
        db.session.commit()

        return jsonify({"success": True}), 200

    return jsonify({"error": "Invalid file"}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete', methods=['POST'])
@login_required
def delete_file():
    if request.method == 'POST':
        filename = request.json.get('filename')

        file = File.query.filter_by(owner_id=current_user.id, filename=filename).first()

        if file:
            # Move the file to the trash folder
            trash_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'trash')
            os.makedirs(trash_folder, exist_ok=True)
            os.rename(
                os.path.join(app.config['UPLOAD_FOLDER'], filename),
                os.path.join(trash_folder, filename)
            )

            # Mark the file as deleted in the database and update the updated_at timestamp
            file.is_deleted = True
            file.updated_at = datetime.utcnow() 
            db.session.commit()

            return jsonify({"success": True}), 200

    return jsonify({"error": "File not found"}), 404

@app.route('/search', methods=['POST'])
@login_required
def search():
    query = request.json.get('query')

    # Get all the files that match the query and exist in the backend folder
    matched_files = File.query.filter(File.filename.contains(query), File.owner_id == current_user.id, File.is_deleted == False).all()
    matched_files = [file for file in matched_files if file_exists(file.filename)]

    
    result = [{"filename": file.filename, "url": url_for('uploaded_file', filename=file.filename)} for file in matched_files]

    return jsonify(result)


@app.route('/delete_all', methods=['POST'])
@login_required
def delete_all_files():
    # Get all trashed files for the current user
    trashed_files = File.query.filter_by(owner_id=current_user.id, is_deleted=True).all()

    # Delete each file permanently from the file system
    for file in trashed_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'trash', file.filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete all trashed files from the database
    File.query.filter_by(owner_id=current_user.id, is_deleted=True).delete()
    db.session.commit()

    return jsonify({"success": True}), 200



if __name__ == '__main__':
    app.run(debug=True)
