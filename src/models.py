from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import string
import random

db= SQLAlchemy()

class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(80), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password= db.Column(db.Text, nullable=False)
    created_at= db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at= db.Column(db.DateTime, nullable=False, onupdate=datetime.now)
    bookmarks= db.relationship('Bookmark', backref='user')

    def __str__(self): 
        return f"User: {self.username}"


class Bookmark(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey("user.id"))
    body= db.Column(db.Text, nullable= True)
    url= db.Column(db.Text, nullable= False)
    short_url= db.Column(db.String(3), nullable= True)
    visits= db.Column(db.Integer, default= 0)
    created_at= db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at= db.Column(db.DateTime, nullable=False, onupdate=datetime.now)

    def generate_short_characters(self):
        characters=  string.digits + string.ascii_letters
        picked_char= ''.join(random.choice(characters, k=3))

        link= self.query.filter_by(short_url= picked_char)

        if link:
            self.generate_short_characters()
        return picked_char




    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url= self.generate_short_characters(kwargs)
    
    def __str__(self): 
        return f"Bookmark: {self.url}"