from flask import Blueprint

bookmarks= Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks/')

@bookmarks.post('/register')
def register():
    return {"bookmarks":[]}

