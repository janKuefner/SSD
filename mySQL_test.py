from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
#the conn_string is used to not hardcode the database credentials
conn_string = "mysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, 
    secrets.dbpass, secrets.dbhost, secrets.dbname)
app.config['SQLALCHEMY_DATABASE_URI'] = conn_string


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)



users = User.query.all()
print()
print('##########')
for user in users:
    print ('User ID: ', user.id)
    print ('Name: ', user.name)
    print ('Role: ', user.role)
    print('##########')

print()
