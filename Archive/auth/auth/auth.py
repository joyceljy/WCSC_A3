from flask import Flask, request
import hashlib
import jwt
from flask_sqlalchemy import SQLAlchemy

tokenKey = "nofearinmyheart"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


@app.before_first_request
def initial():
    db.create_all()


class usersBase(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    userName = db.Column("userName", db.String())
    password = db.Column("password", db.String())

    def __init__(self, userName, password):
        self.userName = userName
        self.password = password


def encryption(oriPassword):
    hl = hashlib.md5()
    hl.update(oriPassword.encode(encoding='utf-8'))
    return hl.hexdigest()

def encode(record):
    data = {'userName': record.userName, 'password': record.password}
    token = jwt.encode(data, tokenKey, algorithm="HS256")
    return token


def decode(token):
    record = jwt.decode(token, tokenKey, algorithms="HS256")
    return record


@app.route('/users', methods=['POST'])
def registration():
    userName = request.form["userName"]
    password = request.form["password"]
    existing_record = usersBase.query.filter_by(userName=userName).first()
    if existing_record:
        return ("User Existed!", 200)
    else:
        db.session.add(usersBase(userName, encryption(password)))
        db.session.commit()
        return ('Registration Success', 200)


@app.route('/users/login', methods=['POST'])
def login():
    userName = request.form["userName"]
    password = request.form["password"]
    existing_record = usersBase.query.filter_by(userName=userName).first()
    if userName == existing_record.userName and encryption(password) == existing_record.password:
        return (encode(existing_record), 200)
    else:
        return('Wrong username or password', 200)


@app.route('/auth', methods=['POST'])
def auth():
    record = decode(request.headers["X-Auth-Token"])
    if not "userName" in record or not "password" in record:
        return ("Forbidden", 403)
    existing_record = usersBase.query.filter_by(
        userName=record["userName"]).first()
    if existing_record.password == record["password"]:
        return (record["userName"], 200)
    else:
        return ("Forbidden", 403)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001, debug=True)
