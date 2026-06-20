import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OrdinalEncoder
import joblib
import os
from datetime import date
from models import Birth, Death

def check_rules(record, record_type):
    anomalies = []
    today = date.today()
    age_years = None
    age_source = ""

    if record_type == 'birth':
        if record.date_of_birth > record.created_at.date():
            anomalies.append({
                'record_type': 'birth',
                'record_id': record.id,
                'anomaly_score': -1.0,
                'details': f"Future birth date (DOB: {record.date_of_birth} > registration date {record.created_at.date()})"
            })
        if record.date_of_birth:
            age_years = (today - record.date_of_birth).days / 365.25
            age_source = f"DOB: {record.date_of_birth}, today: {today}"

    elif record_type == 'death':
        if record.date_of_death > record.created_at.date():
            anomalies.append({
                'record_type': 'death',
                'record_id': record.id,
                'anomaly_score': -1.0,
                'details': f"Future death date (DOD: {record.date_of_death} > registration date {record.created_at.date()})"
            })
        if record.date_of_death > today:
            anomalies.append({
                'record_type': 'death',
                'record_id': record.id,
                'anomaly_score': -1.0,
                'details': f"Future death date (DOD: {record.date_of_death} after today {today})"
            })
        if record.date_of_birth and record.date_of_death:
            age_years = (record.date_of_death - record.date_of_birth).days / 365.25
            age_source = f"DOB: {record.date_of_birth}, DOD: {record.date_of_death}"

    if age_years is not None and age_years > 140:
        anomalies.append({
            'record_type': record_type,
            'record_id': record.id,
            'anomaly_score': -1.0,
            'details': f"Age over 140 ({age_years:.0f} years) – {age_source}"
        })

    return anomalies


def detect_duplicates():
    anomalies = []

    # Duplicate birth detection: same child_name, gender, date_of_birth, mother_name
    births = Birth.query.all()
    seen_birth = {}
    for b in births:
        key = (b.child_name.strip().lower(), b.gender, str(b.date_of_birth), b.mother_name.strip().lower())
        if key in seen_birth:
            # Flag both records as duplicates
            first_id = seen_birth[key]
            # Only flag if not already flagged (to avoid duplicate anomaly rows)
            if not any(a['record_type'] == 'birth' and a['record_id'] == first_id for a in anomalies):
                anomalies.append({
                    'record_type': 'birth',
                    'record_id': first_id,
                    'anomaly_score': -1.0,
                    'details': f"Duplicate birth record (matches registration ID {b.id})"
                })
            anomalies.append({
                'record_type': 'birth',
                'record_id': b.id,
                'anomaly_score': -1.0,
                'details': f"Duplicate birth record (matches registration ID {first_id})"
            })
        else:
            seen_birth[key] = b.id

    # Duplicate death detection: same deceased_name, gender, date_of_birth, date_of_death
    deaths = Death.query.all()
    seen_death = {}
    for d in deaths:
        key = (d.deceased_name.strip().lower(), d.gender, str(d.date_of_birth), str(d.date_of_death))
        if key in seen_death:
            first_id = seen_death[key]
            if not any(a['record_type'] == 'death' and a['record_id'] == first_id for a in anomalies):
                anomalies.append({
                    'record_type': 'death',
                    'record_id': first_id,
                    'anomaly_score': -1.0,
                    'details': f"Duplicate death record (matches registration ID {d.id})"
                })
            anomalies.append({
                'record_type': 'death',
                'record_id': d.id,
                'anomaly_score': -1.0,
                'details': f"Duplicate death record (matches registration ID {first_id})"
            })
        else:
            seen_death[key] = d.id

    return anomalies


def predict_anomalies():
    anomalies = []

    # Rule‑based checks
    births = Birth.query.all()
    deaths = Death.query.all()
    for b in births:
        anomalies.extend(check_rules(b, 'birth'))
    for d in deaths:
        anomalies.extend(check_rules(d, 'death'))

    # Duplicate detection
    anomalies.extend(detect_duplicates())

    return anomalies