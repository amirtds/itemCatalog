from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Category, Item
from sqlalchemy.ext.declarative import declarative_base
from flask import session as login_session
import random
import string
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///itemsCatalog.db')
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)



app = Flask(__name__)

is_authenticated = False

@app.route("/")
def index(is_authenticated):
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template("index.html", categories=categories, items=items)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        try:
            username = request.form['username']
            password = request.form['password']
            session = DBSession()
            user = session.query(User).filter_by(username=username).one()
            if user.verify_password(password):
                is_authenticated = True
                return redirect(url_for('index'))
            else:
                return "Wrong usrname or Password"
        except:
            return "authentication failed"



@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        try:
            username = request.form['username']
            email = request.form['email']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            password = request.form['password']
            session = DBSession()
            newUser = User(
                username = username,
                email = email,
                firstname = firstname,
                lastname = lastname,
            )
            newUser.hash_password(password)
            session.add(newUser)
            session.commit()
            return render_template("index.html")
        except:
            return "registration failed"

@app.route("/catalog/<category_name>")
def show_items_in_category(category_name):
    return render_template("catalogView.html")

@app.route("/items/new", methods=['GET','POST'])
def item_new():
    if request.method == "GET":
        return render_template("itemNew.html")
    else:
        return "Hi post request"

@app.route("/items/edit/<item_name>")
def item_edit(item_name):
    return render_template("itemEdit.html")

@app.route("/items/edit/<item_name>")
def item_delete(item_name):
    return render_template("itemDelete.html")

if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
