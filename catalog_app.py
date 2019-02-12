from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Category, Item
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///itemsCatalog.db')
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)



app = Flask(__name__)



@app.route("/")
def index():
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template("index.html", categories=categories, items=items)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/catalog/<category_name>")
def show_items_in_category(category_name):
    return render_template("catalogView.html")


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
