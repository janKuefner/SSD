################################################################################
### import libraries
################################################################################
### Flask
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import Flask,  send_file
### WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
### SQLalchemy
from flask_sqlalchemy import SQLAlchemy
### file upload
import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
### uuid for filenames in upload folder
import uuid
### database credentials
import secrets_lcl
### file download / move file to another directory
from shutil import copyfile
##ä flask-login
from flask_login import LoginManager, UserMixin, current_user, login_user
from flask_login import logout_user, login_required
### Werkzeut
from werkzeug.security import generate_password_hash, check_password_hash

################################################################################
### start & configure app as well as database
################################################################################
app = Flask(__name__)
### WTForms
app.config['SECRET_KEY'] = secrets_lcl.secret_key
### file upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
### SQLalchemy
conn_string = "mysql://{0}:{1}@{2}/{3}".format(secrets_lcl.dbuser, 
    secrets_lcl.dbpass, secrets_lcl.dbhost, secrets_lcl.dbname)
app.config['SQLALCHEMY_DATABASE_URI'] = conn_string
db = SQLAlchemy(app)
### flask-login
login = LoginManager(app)
login.login_view = 'login'


################################################################################
### class definitions
################################################################################
'''User class is enhanced by UserMixin. UserMixin brings attributes like 
is_authenticated etc. which are use by flask-login'''
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    confidential = db.Column(db.Boolean, unique=True, nullable=False)
    uploader = db.Column(db.String(50), unique=True, nullable=False)
    storage_name = db.Column(db.String(50), unique=True, nullable=False)
    short_description_of_file =  db.Column( 
     db.String(201),
     unique=True,
     nullable=False
    )

'''Flask-Login needs a user_loader function, that returns the user object of a 
user with a certain id, so here we go:'''
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#read out backend at app startup
users = User.query.all()
datas = Data.query.all()



################################################################################
# file download
################################################################################
# decrypt function used at file downlaod
def decrypt_file_in_flush_folder(filename):
    from cryptography.fernet import Fernet
    key = open("key.key", "rb").read() #load key for encryption
    # initialize the Fernet class
    f = Fernet(key)
    with open("flush/" + filename, "rb") as file:
        # read all file data
        encrypted_data = file.read()
    # encrypt data
    decrypted_data = f.decrypt(encrypted_data)
    # write the encrypted file
    with open("flush/" + filename, "wb") as file:
        file.write(decrypted_data)

#download file (not a page, send_file action)
@app.route('/download')
@login_required
def return_files():
    datas = Data.query.all()
    for data in datas:
        if str(data.id) == request.args.get('id'):
            file_name=data.name 
            storage_name=data.storage_name
    #copy file to flush folder for decryption
    copyfile('upload/'+storage_name, 'flush/'+file_name)
    decrypt_file_in_flush_folder(file_name)
    #os.remove('flush/'+file_name_string)
    return send_file('flush/' + file_name, 
        download_name=file_name)
        

################################################################################
# delete file - only intermittend page
################################################################################
### delete file PAGE - Note: just an intermittend page, 
### the real deletion will be done at index.html
@app.route('/delete')
@login_required
def delete():
    kil=(request.args.get('del'))
    return render_template('delete.html', kil=kil)

################################################################################
# index / show files (can also update and delete data entries)
################################################################################
### show files PAGE
@app.route('/')
@app.route('/index')
@login_required
def index():
    datas = Data.query.all()
    users = User.query.all()
    #delete data entry
    kil=(request.args.get('kil'))
    if kil != None:
        for data in datas:
            if data.id == int(kil):
                os.remove('upload/'+ data.storage_name)
        Data.query.filter_by(id=kil).delete()
        flash('File successfully deleted')
        datas = Data.query.all()
        db.session.commit()
    #update
    updt = (request.args.get('updt'))
    if updt != None:
        updt=int(updt)
        entry_to_delete = Data.query.filter_by(id=updt).first()
        entry_to_delete.uploader = 'deleted'
        flash('File successfully updated')
        datas = Data.query.all()
        db.session.commit()
    return render_template('index.html', datas=datas, users=users)
    
################################################################################
# file upload 
################################################################################
# function used in file upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# encrypt function used in file upload
def encrypt_file_in_upload_folder(filename):
    from cryptography.fernet import Fernet
    key = open("key.key", "rb").read() #load key for encryption
    # initialize the Fernet class
    f = Fernet(key)
    with open("upload/" + filename, "rb") as file:
        # read all file data
        file_data = file.read()
    # encrypt data
    encrypted_data = f.encrypt(file_data)
    # write the encrypted file
    with open("upload/" + filename, "wb") as file:
        file.write(encrypted_data)

### upload PAGE
@app.route('/upload', methods=['GET','POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
        #display error message, if filetype not okay
        if file and allowed_file(file.filename)==False:
            flash('Filetype not permitted')
        #upload and encrypt, if all is cool.
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            storage_name = (filename + '_' + str(uuid.uuid4()))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], storage_name))
            encrypt_file_in_upload_folder(storage_name)
            last_add = Data(
                name=filename, 
                confidential=0, 
                uploader=current_user.id,
                storage_name=storage_name
                )
            db.session.add(last_add)
            db.session.commit()
            flash('File uploaded and encrypted')
            return redirect(url_for('metadata'))
    return render_template('upload.html')

################################################################################
# Metadata add / update
################################################################################
### class used for add metadata
class MetadataForm(FlaskForm):
    short_description = StringField()
    confidential = BooleanField()
    submit = SubmitField('add metadata')

### metadata PAGE
@app.route('/metadata', methods=['GET','POST'])
@login_required
def metadata():
    form = MetadataForm()
    if form.validate_on_submit():
        id_from_get=(request.args.get('id'))
        if id_from_get == None:
            datas = Data.query.all()
            for data in datas:
                id_from_get = data.id
                print(id_from_get)
        data_to_change = Data.query.filter_by(id=id_from_get).first()
        data_to_change.short_description_of_file = form.short_description.data
        if form.confidential.data == True:
            data_to_change.confidential = 1
        else:
            data_to_change.confidential = 0
        db.session.commit()
        flash('Metadata added / updated')
        return redirect('/index')
    return render_template('metadata.html', form=form)    


################################################################################
# Login
################################################################################
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    from werkzeug.security import check_password_hash
    from werkzeug.security import generate_password_hash
    '''check if user.name and user.password entry is not a match and redirect 
    to login page with flash massage'''
    if form.validate_on_submit():
        users = User.query.all()
        '''check, if there is a username and password matach aka if user can be 
        authenticated'''
        for user in users:
            if user.name == form.username.data:
                if check_password_hash (user.password, form.password.data):
                    authenticated_user=user
                    login_user(authenticated_user,
                     remember=form.remember_me.data)
                    return redirect('/index')      
        #if no match, flash error and redirect to login again
        flash('Login failed')
        return redirect('login')
    return render_template('login.html', form=form)

################################################################################
# logout
################################################################################
@app.route('/logout')
def logout():
    logout_user()
    return redirect('login')


################################################################################
### User registration
################################################################################
class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    password2 = PasswordField(validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

### Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('index')
    form = RegistrationForm()
    if form.validate_on_submit():
        users = User.query.all()
        #check if user name already exists
        for user in users:
            if user.name == form.username.data:
                flash('Username is already taken, please pick another one')
                return redirect('register')
        #check if the E-Mail already exists
        for user in users:
            if user.email == form.email.data:
                flash('Ups, someone already registered with this E-Mail.')
                return redirect('register')
        #if all well
        user_to_be_added = User(
            name=form.username.data, 
            password=generate_password_hash(form.password.data, 'sha256'), 
            email=form.email.data,
            role = '0'
        )
        db.session.add(user_to_be_added)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect('login')
    return render_template('register.html', form=form)


################################################################################
# start the web app
################################################################################
if __name__ == '__main__':
    app.run()