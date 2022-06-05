from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flasgger import swag_from

from werkzeug.security import check_password_hash, generate_password_hash
import validators

from src.constants.http_status_codes import *
from src.models import User, db

auth= Blueprint('auth', __name__, url_prefix='/api/v1/auth/')

@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    username= request.json["username"]
    email= request.json["email"]
    password= request.json["password"]

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

    password_hash= generate_password_hash(password)
    user= User(username=username, password= password_hash, email=email) 
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
        'message': "User created",
        'user': {'username': username, "email": email}
        }
        ), HTTP_201_CREATED


@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email= request.json.get("email", None)
    password= request.json.get("password", None)

    user= User.query.filter_by(email=email).first()

    if user:
        check_pass= check_password_hash(user.password, password)

        if check_pass:
            refresh= create_refresh_token(identity= user.id)
            access= create_access_token(identity= user.id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
                }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

@auth.get('/me') 
@jwt_required()
def me():
    user_id= get_jwt_identity()
    user= User.query.get(user_id)

    return jsonify({
        "username": user.username,
        "email": user.email
    }), HTTP_200_OK

@auth.get('/token/refresh')
@jwt_required(refresh= True)
def refresh_users_token():
    user_id= get_jwt_identity()
    access= create_access_token(identity= user_id)

    return jsonify({"access": access}), HTTP_200_OK

