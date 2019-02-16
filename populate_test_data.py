from database_setup import User, Category, Item
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_string = 'postgresql://catalogapp:O2NwGz8O5wd73Qkq6K2nxSCfFPSa5O5Y@localhost:5432/catalog'
engine = create_engine(db_string)
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

newUser = User(
                id = 1,
                username = "amir",
                email = "amirtds@gmail.com",
                firstname = "amir",
                lastname = "tadrisi",
                )
newUser.hash_password("qd8@!V-%$#iW")
session.add(newUser)

newCategory = Category(
                        id = 1,
                        name="IT",
                        description="Articles related to computers",
                        created_by_id=newUser.id,
                        )
session.add(newCategory)

newItem = Item(
                id = 1,
                name="Flask programming",
                category_id=newCategory.id,
                created_by_id=newUser.id,
                description="Flask programming is awesome and easy",
                )
session.add(newItem)


newUser = User(
                id = 2,
                username = "John",
                email = "John@gmail.com",
                firstname = "John",
                lastname = "Doe",
                )
newUser.hash_password("qd8@!V-dasd%$#a1iW")
session.add(newUser)

newCategory = Category(
                        id = 2,
                        name="Sport",
                        description="Articles related to sports",
                        created_by_id=newUser.id,
                        )
newItem = Item(
                id = 2,
                name="Soccer",
                category_id=newCategory.id,
                created_by_id=newUser.id,
                description="World cup 2022",
                )

session.add(newCategory)
session.add(newItem)
session.commit()
