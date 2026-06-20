from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Death, AuditLog
from datetime import datetime

deaths_bp = Blueprint('deaths', __name__)

@deaths_bp.route('/deaths', methods=['POST'])
@jwt_required()
def create_death():
    data = request.get_json()
    death = Death(
        registration_number=data['registration_number'],
        deceased_name=data['deceased_name'],
        gender=data['gender'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d'),
        date_of_death=datetime.strptime(data['date_of_death'], '%Y-%m-%d'),
        cause_of_death=data['cause_of_death'],
        county=data['county'],
        sub_county=data['sub_county'],
        informant_name=data['informant_name']
    )
    db.session.add(death)
    log = AuditLog(user_id=get_jwt_identity(), action=f"Created death record {death.registration_number}")
    db.session.add(log)
    db.session.commit()
    return jsonify(msg="Death registered", id=death.id), 201

@deaths_bp.route('/deaths', methods=['GET'])
@jwt_required()
def get_deaths():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Death.query
    county_filter = request.args.get('county')
    if county_filter:
        query = query.filter_by(county=county_filter)
    deaths = query.order_by(Death.created_at.desc()).paginate(page=page, per_page=per_page)
    result = [{
        'id': d.id,
        'registration_number': d.registration_number,
        'deceased_name': d.deceased_name,
        'gender': d.gender,
        'date_of_birth': d.date_of_birth.isoformat(),
        'date_of_death': d.date_of_death.isoformat(),
        'cause_of_death': d.cause_of_death,
        'county': d.county,
        'sub_county': d.sub_county,
        'informant_name': d.informant_name,
        'created_at': d.created_at.isoformat()
    } for d in deaths.items]
    return jsonify(data=result, total=deaths.total, pages=deaths.pages, current_page=page), 200

@deaths_bp.route('/deaths/<int:id>', methods=['GET'])
@jwt_required()
def get_death(id):
    death = Death.query.get_or_404(id)
    return jsonify({
        'id': death.id,
        'registration_number': death.registration_number,
        'deceased_name': death.deceased_name,
        'gender': death.gender,
        'date_of_birth': death.date_of_birth.isoformat(),
        'date_of_death': death.date_of_death.isoformat(),
        'cause_of_death': death.cause_of_death,
        'county': death.county,
        'sub_county': death.sub_county,
        'informant_name': death.informant_name,
        'created_at': death.created_at.isoformat()
    }), 200

@deaths_bp.route('/deaths/<int:id>', methods=['PUT'])
@jwt_required()
def update_death(id):
    death = Death.query.get_or_404(id)
    data = request.get_json()
    death.registration_number = data.get('registration_number', death.registration_number)
    death.deceased_name = data.get('deceased_name', death.deceased_name)
    death.gender = data.get('gender', death.gender)
    if 'date_of_birth' in data:
        death.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
    if 'date_of_death' in data:
        death.date_of_death = datetime.strptime(data['date_of_death'], '%Y-%m-%d')
    death.cause_of_death = data.get('cause_of_death', death.cause_of_death)
    death.county = data.get('county', death.county)
    death.sub_county = data.get('sub_county', death.sub_county)
    death.informant_name = data.get('informant_name', death.informant_name)
    db.session.commit()
    return jsonify(msg="Death updated"), 200
