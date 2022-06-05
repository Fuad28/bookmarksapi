from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.constants.http_status_codes import *
from src.models import Bookmark, db

import validators

bookmarks= Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks/')

@bookmarks.route('/', methods=['GET', 'POST'])
@jwt_required()
def bookmarks_route():
    current_user= get_jwt_identity()

    if request.method == 'POST':
        body= request.json.get("body", '')
        url= request.json.get("url", '')
        if not validators.url(url):
            return jsonify({'error': "Enter valid url"}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url= url).first():
            return jsonify({'error': "Url exists"}), HTTP_409_CONFLICT

        bookmark = Bookmark(url= url, body= body, user_id= current_user)

        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            "id": bookmark.id,
            "url": bookmark.url,
            "short_url": bookmark.short_url,
            "visits": bookmark.visits,
            "body": bookmark.body,
            "created_at": bookmark.created_at,
            "updated_at": bookmark.updated_at,
        }), HTTP_201_CREATED
    
    else:
        page= request.args.get('page', 1, type= int)
        per_page= request.args.get('per_page', 5, type= int)


        bookmarks= Bookmark.query.filter_by(user_id= current_user).paginate(page= page, per_page=per_page)

        data= [
            {
                "id": bookmark.id,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "body": bookmark.body,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at
            }
            for bookmark in bookmarks.items
        ]

        meta= {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "prev_page": bookmarks.prev_num,
            "next_page": bookmarks.next_num,
            "has_next": bookmarks.has_next,
            "has_prev": bookmarks.has_prev,

        }

        return jsonify({"data": data, "meta": meta}), HTTP_200_OK

@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user= get_jwt_identity()
    
    bookmark= Bookmark.query.filter_by(user_id= current_user, id= id).first()

    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), HTTP_404_NOT_FOUND
    

    return jsonify({
        "id": bookmark.id,
        "url": bookmark.url,
        "short_url": bookmark.short_url,
        "visits": bookmark.visits,
        "body": bookmark.body,
        "created_at": bookmark.created_at,
        "updated_at": bookmark.updated_at 

        }), HTTP_200_OK

@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def edit_bookmark(id):
    current_user= get_jwt_identity()
    
    bookmark= Bookmark.query.filter_by(user_id= current_user, id= id).first()

    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), HTTP_404_NOT_FOUND

    body= request.json.get("body", '')
    url= request.json.get("url", '')

    if not validators.url(url):
        return jsonify({'error': "Enter valid url"}), HTTP_400_BAD_REQUEST

    if Bookmark.query.filter_by(url= url).first():
        return jsonify({'error': "Url exists"}), HTTP_409_CONFLICT


    bookmark.body = body
    bookmark.url = url

    db.session.commit()

    return jsonify({
        "id": bookmark.id,
        "url": bookmark.url,
        "short_url": bookmark.short_url,
        "visits": bookmark.visits,
        "body": bookmark.body,
        "created_at": bookmark.created_at,
        "updated_at": bookmark.updated_at 

        }), HTTP_200_OK


@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user= get_jwt_identity()
    
    bookmark= Bookmark.query.filter_by(user_id= current_user, id= id).first()

    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@bookmarks.get("/stats")
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK