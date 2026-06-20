from flask import Blueprint, send_file, request
from flask_jwt_extended import jwt_required
from models import Birth, Death
from fpdf import FPDF
import csv
import io
import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/export/csv/births', methods=['GET'])
@jwt_required()
def export_births_csv():
    births = Birth.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Reg Number', 'Child Name', 'Gender', 'Date of Birth', 'County', 'Sub County', 'Mother', 'Father'])
    for b in births:
        writer.writerow([b.registration_number, b.child_name, b.gender, b.date_of_birth, b.county, b.sub_county, b.mother_name, b.father_name])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='births.csv')

@reports_bp.route('/export/csv/deaths', methods=['GET'])
@jwt_required()
def export_deaths_csv():
    deaths = Death.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Reg Number', 'Deceased Name', 'Gender', 'DOB', 'DOD', 'Cause', 'County', 'Sub County', 'Informant'])
    for d in deaths:
        writer.writerow([d.registration_number, d.deceased_name, d.gender, d.date_of_birth, d.date_of_death, d.cause_of_death, d.county, d.sub_county, d.informant_name])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='deaths.csv')

@reports_bp.route('/export/pdf/births', methods=['GET'])
@jwt_required()
def export_births_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Kenya Birth Registry Report", ln=True, align='C')
    pdf.ln(10)
    births = Birth.query.all()
    for b in births:
        pdf.cell(200, 10, txt=f"{b.registration_number} - {b.child_name} ({b.gender}) DOB: {b.date_of_birth} County: {b.county}", ln=True)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return send_file(io.BytesIO(pdf_output), mimetype='application/pdf', as_attachment=True, download_name='births_report.pdf')

@reports_bp.route('/export/pdf/deaths', methods=['GET'])
@jwt_required()
def export_deaths_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Kenya Death Registry Report", ln=True, align='C')
    pdf.ln(10)
    deaths = Death.query.all()
    for d in deaths:
        pdf.cell(200, 10, txt=f"{d.registration_number} - {d.deceased_name} ({d.gender}) DOD: {d.date_of_death} Cause: {d.cause_of_death}", ln=True)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return send_file(io.BytesIO(pdf_output), mimetype='application/pdf', as_attachment=True, download_name='deaths_report.pdf')
