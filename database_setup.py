from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    password_hashed = Column(String(250), nullable=False)
    date_joined = Column(DateTime, nullable=False, default=datetime.utcnow)

    def hash_password(self, password):
        self.password_hashed = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hashed)

    @property
    def serialize(self):
        return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'firstname': self.firstname,
                'lastname': self.lastname,
                'date_joined': self.date_joined,
        }


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(250), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship(User)

    def serialize(self, items):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'created_by': self.created_by.username,
                'items': [
                          item.serialize
                          for item in items
                          if item.category.name == self.name
                        ]
                }


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship(User)
    description = Column(String(250), nullable=False)
    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)

    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'category': self.category.name,
                'description': self.description
                }


engine = create_engine('sqlite:///itemsCatalog.db')
Base.metadata.create_all(engine)
