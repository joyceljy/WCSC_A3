import re
from flask import Flask, render_template, request, redirect, abort
import jwt
from flask_sqlalchemy import SQLAlchemy
import random
import string
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
tokenKey = "nofearinmyheart"
db = SQLAlchemy(app)


@app.before_first_request
def initial():
    db.create_all()


class urlBase(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    realURL = db.Column("realURL", db.String())
    shortURL = db.Column("shortURL", db.String())
    userName = db.Column("userName", db.String())

    def __init__(self, realURL, shortURL, userName):
        self.realURL = realURL
        self.shortURL = shortURL
        self.userName = userName


def id_generating():
    while True:
        ran_str = ''.join(random.sample(
            string.ascii_letters + string.digits, 8))
        existing_record = urlBase.query.filter_by(shortURL=ran_str).first()
        if not existing_record:
            return ran_str
        return ran_str

def decode(token):
    record = jwt.decode(token, tokenKey, algorithms="HS256")
    return record

def auth(token):
    data = {"X-Auth-Token": token}
    # record = requests.post("http://127.0.0.1:5001/auth", headers=data)
    record = decode(token)
    if not "userName" in record or not "password" in record:
        return 'a'
    else:
        return (record["userName"])


@app.route('/', methods=['POST', 'GET', 'PUT', 'DELETE'])
def postman():
    if "X-Auth-Token" in request.headers:
        userName = auth(request.headers["X-Auth-Token"])
    else:
        return('Please Log In First', 403)
    if request.method == "POST":
        input_url = request.form["realURL"]
        existing_record = urlBase.query.filter_by(realURL=input_url).first()
        if existing_record:
            return render_template("result.html", shortURL=request.url+existing_record.shortURL)
        else:
            shortURL = id_generating()
            db.session.add(urlBase(input_url, shortURL, userName))
            db.session.commit()
            return render_template("result.html", shortURL=request.url+shortURL)

    elif request.method == "GET":
        existing_record = urlBase.query.filter_by(userName=userName).all()
        return render_template("showall.html", allurl=existing_record)
    elif request.method == "DELETE":
        input_url = request.form["realURL"]
        existing_record = urlBase.query.filter_by(realURL=input_url).first()
        if existing_record and existing_record.userName == userName:
            urlBase.query.filter_by(realURL=input_url).delete()
            db.session.commit()
            db.session.close()
            return ("success", 204)
        if not existing_record.userName == userName:
            return ("Forbidden", 403)
        else:
            abort(404)
    elif request.method == "PUT":
        input_url = request.form["realURL"]
        existing_record = urlBase.query.filter_by(realURL=input_url).first()
        if existing_record and existing_record.userName == userName:
            existing_record.shortURL = request.form["shortURL"]
            db.session.commit()
            db.session.close()
            return ("successfully updated", 204)
        if not existing_record.userName == userName:
            return ("Forbidden", 403)
        else:
            abort(404)


@app.route('/<shortURL>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def redirection(shortURL):
    if not request.method == "GET":
        if "X-Auth-Token" in request.headers:
            userName = auth(request.headers["X-Auth-Token"])
        else:
            return('Please Log In First', 403)
    if request.method == "GET":
        existing_record = urlBase.query.filter_by(shortURL=shortURL).first()
        if existing_record:
            return redirect(existing_record.realURL)
        else:
            abort(404)
    elif request.method == "DELETE":
        existing_record = urlBase.query.filter_by(shortURL=shortURL).first()
        if existing_record and existing_record.userName == userName:
            urlBase.query.filter_by(shortURL=shortURL).delete()
            db.session.commit()
            db.session.close()
            return "success", 204
        if not existing_record.userName == userName:
            return ("Forbidden", 403)
        else:
            abort(404)
    elif request.method == "PUT":
        input_url = request.form["realURL"]
        if not re.match("(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", input_url, flags=0):
            return "Invalid URL", 400

        existing_record = urlBase.query.filter_by(shortURL=shortURL).first()
        if existing_record and existing_record.userName == userName:
            existing_record.realURL = input_url
            db.session.commit()
            db.session.close()
            return ("success", 204)
        if not existing_record.userName == userName:
            return ("Forbidden", 403)

        else:
            abort(404)


@app.route('/homepage', methods=['POST', 'GET', 'PUT', 'DELETE'])
def homepage():
    return app.send_static_file("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
