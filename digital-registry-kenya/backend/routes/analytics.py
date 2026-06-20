from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import db, Birth, Death
from sqlalchemy import func, extract

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/summary', methods=['GET'])
@jwt_required()
def summary():
    total_births = Birth.query.count()
    total_deaths = Death.query.count()
    counties = db.session.query(Birth.county).distinct().count()
    return jsonify(total_births=total_births, total_deaths=total_deaths, counties=counties)

@analytics_bp.route('/analytics/births-per-county', methods=['GET'])
@jwt_required()
def births_per_county():
    results = db.session.query(Birth.county, func.count(Birth.id)).group_by(Birth.county).all()
    data = [{'county': r[0], 'count': r[1]} for r in results]
    return jsonify(data)

@analytics_bp.route('/analytics/deaths-per-county', methods=['GET'])
@jwt_required()
def deaths_per_county():
    results = db.session.query(Death.county, func.count(Death.id)).group_by(Death.county).all()
    data = [{'county': r[0], 'count': r[1]} for r in results]
    return jsonify(data)

@analytics_bp.route('/analytics/monthly-trends', methods=['GET'])
@jwt_required()
def monthly_trends():
    births = db.session.query(extract('month', Birth.created_at).label('month'), extract('year', Birth.created_at).label('year'), func.count(Birth.id)).group_by('year', 'month').order_by('year', 'month').all()
    deaths = db.session.query(extract('month', Death.created_at).label('month'), extract('year', Death.created_at).label('year'), func.count(Death.id)).group_by('year', 'month').order_by('year', 'month').all()
    return jsonify(births=[{'month': f"{b[1]}-{b[0]:02d}", 'count': b[2]} for b in births],
                   deaths=[{'month': f"{d[1]}-{d[0]:02d}", 'count': d[2]} for d in deaths])

@analytics_bp.route('/analytics/gender-stats', methods=['GET'])
@jwt_required()
def gender_stats():
    birth_gender = db.session.query(Birth.gender, func.count(Birth.id)).group_by(Birth.gender).all()
    death_gender = db.session.query(Death.gender, func.count(Death.id)).group_by(Death.gender).all()
    return jsonify(births=[{'gender': g[0], 'count': g[1]} for g in birth_gender],
                   deaths=[{'gender': g[0], 'count': g[1]} for g in death_gender])
    