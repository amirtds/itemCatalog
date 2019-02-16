from flask import Flask, render_template, url_for
from flask import request, redirect, flash, jsonify, session, g
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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


engine = create_engine('sqlite:///itemsCatalog.db')
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


app = Flask(__name__)
# Limiting api calls with limiter lib
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"]
)


@app.route("/")
def index(is_authenticated=False):
    dbsession = DBSession()
    categories = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    return render_template("index.html", categories=categories, items=items)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        try:
            # get username and password user input in the login form
            username = request.form['username']
            password = request.form['password']
            # clean up any session
            session.pop('user', None)
            dbsession = DBSession()
            user = dbsession.query(User).filter_by(username=username).one()
            # verify user's input passwrd with the password in DB
            if user.verify_password(password):
                # set the session if the credentials is right
                session['user'] = username
                return redirect(url_for("index"))
            else:
                return redirect(url_for("login"))
        except Exception as e:
            return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # clean up the session
    session.pop('user', None)
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        try:
            # get new user's information from the form
            username = request.form['username']
            email = request.form['email']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            password = request.form['password']
            # create user based on input inf in form
            dbsession = DBSession()
            newUser = User(
                username=username,
                email=email,
                firstname=firstname,
                lastname=lastname,
            )
            # save hashed form of the input password in db
            newUser.hash_password(password)
            dbsession.add(newUser)
            dbsession.commit()
            return render_template("index.html")
        except Exception as e:
            return redirect(url_for("register"))


@app.route("/categories/new", methods=['GET', 'POST'])
def category_new():
    if session:
        if request.method == "GET":
            return render_template("categoryNew.html")
        elif request.method == "POST":
            # create new category based user's input in categoryNew
            category_name = request.form['category_name']
            category_description = request.form['category_description']
            dbsession = DBSession()
            creator = dbsession.query(User).filter_by(
                                                      username=session['user']
                                                      ).one()
            newCategory = Category(
                                   name=category_name,
                                   description=category_description,
                                   created_by_id=creator.id
                                   )
            dbsession.add(newCategory)
            dbsession.commit()
            return redirect(url_for("index"))
    else:
        return redirect(url_for('login'))


@app.route("/items/new", methods=['GET', 'POST'])
def item_new():
    if session:
        dbsession = DBSession()
        categories = dbsession.query(Category).all()
        items = dbsession.query(Item).all()
        if request.method == "GET":
            return render_template(
                                    "itemNew.html",
                                    categories=categories,
                                    items=items
                                )
        elif request.method == "POST":
            # create new category based user's input
            newItemName = request.form['item_name']
            newItemDescription = request.form['item_description']
            newItemCategory = request.form['item_category']
            creator = dbsession.query(User).filter_by(
                                                    username=session['user']
                                                    ).one()
            category = dbsession.query(Category).filter_by(
                                                    name=newItemCategory
                                                    ).one()
            newItem = Item(name=newItemName,
                           category_id=category.id,
                           created_by_id=creator.id,
                           description=newItemDescription)
            dbsession.add(newItem)
            dbsession.commit()
            return redirect(url_for("index"))
    else:
        return redirect(url_for('login'))


@app.route("/items/edit/<item_name>", methods=['GET', 'POST'])
def item_edit(item_name):
    if session:
            dbsession = DBSession()
            dbsession = DBSession()
            item = dbsession.query(Item).filter_by(name=item_name).one()
            categories = dbsession.query(Category).all()
            if session['user'] == item.created_by.username :
                if request.method == "GET":
                    return render_template(
                                            "itemEdit.html",
                                            item=item,
                                            categories=categories)
                elif request.method == "POST":

                        editItemName = request.form['item_name']
                        editItemDescription = request.form['item_description']
                        editItemCategory = request.form['item_category']
                        category = dbsession.query(Category).filter_by(
                                                                    name=editItemCategory
                                                                    ).one()
                        item.name = editItemName
                        item.description = editItemDescription
                        item.category_id = category.id
                        dbsession.add(item)
                        dbsession.commit()
                        return redirect(url_for("index"))
            else:
                return redirect(url_for("index"))
    else:
        return redirect(url_for('login'))


@app.route("/items/delete/<item_name>", methods=['GET', 'POST'])
def item_delete(item_name):
    if session:
        dbsession = DBSession()
        item = dbsession.query(Item).filter_by(name=item_name).one()
        if session['user'] == item.created_by.username :
            if request.method == "GET":
                return render_template("itemDelete.html", item=item)
            elif request.method == "POST":
                dbsession.delete(item)
                dbsession.commit()
                return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
    else:
        redirect(url_for("login"))


@app.route("/api/catalog.json")
# rate limit the api
@limiter.limit("100 per day")
def catalog_json():
    dbsession = DBSession()
    categories = dbsession.query(Category).all()
    items = dbsession.query(Item).all()
    categories_list = [category.serialize(items) for category in categories]
    # return json of catagories with their items
    return jsonify(Categories=categories_list)


if __name__ == "__main__":
    app.secret_key = 'ni8Ou19UcJwvy2ozE1CEVHGlOXEcjKfO'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
