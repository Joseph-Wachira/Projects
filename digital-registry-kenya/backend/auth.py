from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'county': user.county})
        return jsonify(token=token, role=user.role, county=user.county), 200
    return jsonify(msg="Invalid credentials"), 401

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    claims = get_jwt_identity()
    user = User.query.get(int(claims))
    if user and user.role != 'admin':
        return jsonify(msg="Admin access required"), 403
    data = request.get_json()
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'registrar'),
        county=data.get('county')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(msg="User created"), 201
