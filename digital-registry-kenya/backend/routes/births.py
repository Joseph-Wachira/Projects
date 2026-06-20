from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Birth, AuditLog
from datetime import datetime

births_bp = Blueprint('births', __name__)

@births_bp.route('/births', methods=['POST'])
@jwt_required()
def create_birth():
    data = request.get_json()
    birth = Birth(
        registration_number=data['registration_number'],
        child_name=data['child_name'],
        gender=data['gender'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d'),
        county=data['county'],
        sub_county=data['sub_county'],
        mother_name=data['mother_name'],
        father_name=data.get('father_name', '')
    )
    db.session.add(birth)
    log = AuditLog(user_id=get_jwt_identity(), action=f"Created birth record {birth.registration_number}")
    db.session.add(log)
    db.session.commit()
    return jsonify(msg="Birth registered", id=birth.id), 201

@births_bp.route('/births', methods=['GET'])
@jwt_required()
def get_births():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Birth.query
    county_filter = request.args.get('county')
    if county_filter:
        query = query.filter_by(county=county_filter)
    births = query.order_by(Birth.created_at.desc()).paginate(page=page, per_page=per_page)
    result = [{
        'id': b.id,
        'registration_number': b.registration_number,
        'child_name': b.child_name,
        'gender': b.gender,
        'date_of_birth': b.date_of_birth.isoformat(),
        'county': b.county,
        'sub_county': b.sub_county,
        'mother_name': b.mother_name,
        'father_name': b.father_name,
        'created_at': b.created_at.isoformat()
    } for b in births.items]
    return jsonify(data=result, total=births.total, pages=births.pages, current_page=page), 200

@births_bp.route('/births/<int:id>', methods=['GET'])
@jwt_required()
def get_birth(id):
    birth = Birth.query.get_or_404(id)
    return jsonify({
        'id': birth.id,
        'registration_number': birth.registration_number,
        'child_name': birth.child_name,
        'gender': birth.gender,
        'date_of_birth': birth.date_of_birth.isoformat(),
        'county': birth.county,
        'sub_county': birth.sub_county,
        'mother_name': birth.mother_name,
        'father_name': birth.father_name,
        'created_at': birth.created_at.isoformat()
    }), 200

@births_bp.route('/births/<int:id>', methods=['PUT'])
@jwt_required()
def update_birth(id):
    birth = Birth.query.get_or_404(id)
    data = request.get_json()
    birth.registration_number = data.get('registration_number', birth.registration_number)
    birth.child_name = data.get('child_name', birth.child_name)
    birth.gender = data.get('gender', birth.gender)
    if 'date_of_birth' in data:
        birth.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
    birth.county = data.get('county', birth.county)
    birth.sub_county = data.get('sub_county', birth.sub_county)
    birth.mother_name = data.get('mother_name', birth.mother_name)
    birth.father_name = data.get('father_name', birth.father_name)
    db.session.commit()
    return jsonify(msg="Birth updated"), 200
