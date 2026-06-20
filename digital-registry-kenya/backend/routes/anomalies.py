from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import db, Anomaly, Birth, Death
import ai_anomaly

anomalies_bp = Blueprint('anomalies', __name__)


@anomalies_bp.route('/anomalies/scan', methods=['POST'])
@jwt_required()
def scan():
    anomalies = ai_anomaly.predict_anomalies()

    Anomaly.query.delete()

    for a in anomalies:
        db.session.add(Anomaly(
            record_type=a['record_type'],
            record_id=a['record_id'],
            anomaly_score=a['anomaly_score'],
            details=a['details']
        ))

    db.session.commit()

    return jsonify(
        message=f"Scan complete. {len(anomalies)} anomalies found.",
        count=len(anomalies)
    ), 200


@anomalies_bp.route('/anomalies', methods=['GET'])
@jwt_required()
def list_anomalies():
    anomalies = Anomaly.query.order_by(Anomaly.anomaly_score).all()
    result = []
    for a in anomalies:
        record_info = None
        if a.record_type == 'birth':
            b = Birth.query.get(a.record_id)
            if b:
                record_info = {
                    'registration_number': b.registration_number,
                    'name': b.child_name,
                    'date_of_birth': b.date_of_birth.isoformat(),
                    'county': b.county,
                    'sub_county': b.sub_county,
                    'gender': b.gender
                }
        elif a.record_type == 'death':
            d = Death.query.get(a.record_id)
            if d:
                record_info = {
                    'registration_number': d.registration_number,
                    'name': d.deceased_name,
                    'date_of_birth': d.date_of_birth.isoformat(),
                    'date_of_death': d.date_of_death.isoformat(),
                    'county': d.county,
                    'sub_county': d.sub_county,
                    'cause_of_death': d.cause_of_death
                }
        result.append({
            'id': a.id,
            'record_type': a.record_type,
            'record_id': a.record_id,
            'anomaly_score': a.anomaly_score,
            'details': a.details,
            'created_at': a.created_at.isoformat(),
            'record_info': record_info
        })
    return jsonify(result)