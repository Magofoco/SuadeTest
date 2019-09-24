from flask import Flask, request, jsonify, render_template, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
import sys
import psycopg2 as db
from flask import abort
import json
import pdfkit

app = Flask(__name__)

# conn = db.connect(host='candidate.suade.org', database='suade', user='interview', password='uo4uu3AeF3', port='5432')
# cur = conn.cursor()
# reports = cur.execute("SELECT * FROM reports")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://interview:uo4uu3AeF3@candidate.suade.org/suade'
db = SQLAlchemy(app)
results = db.engine.execute("SELECT * FROM reports")
reports = [dict(r) for r in results if r["id"] != 5]
for r in reports:
    r['type'] = json.loads(r['type'])

existing_reports_id = [report["id"] for report in reports]


# The controllers for the templates
@app.route('/')
def home():
  return render_template("home.html")

@app.route('/allreports')
def allreports():
  return render_template("allreports.html", reports=reports)

@app.route('/allreports/<int:report_id>')
def reportdetail(report_id):
  report = [report for report in reports if report['id'] == report_id]
  if len(report) == 0 or report_id not in existing_reports_id or report_id==5:
      return("The report ID does not exist. Go back.")
  return render_template("reportdetail.html", report=report[0])

@app.route('/allreports/<int:report_id>/pdf')
def pdf_template(report_id):
  report = [report for report in reports if report['id'] == report_id]
  rendered = render_template('reportdetail.html', report=report[0])
  css = ['static/main.css']
  pdf = pdfkit.from_string(rendered, False, css=css)
  response = make_response(pdf)
  response.headers["Content-Type"] = "application/pdf"
  response.headers["Content-Disposition"] = 'inline; filename=pdfoutput.pdf'
  return response

@app.route('/allreports/<int:report_id>/xml')
def xml_template(report_id):
  report = [report for report in reports if report['id'] == report_id]
  template = render_template('reportdetail.html', report=report[0])
  response = make_response(template)
  response.headers['Content-Type'] = 'application/xml'
  return response


# The API endpoints

@app.route('/api/reports', methods=['GET'])
def get_reports():
    return jsonify({'reports': reports})

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    report = [report for report in reports if report['id'] == report_id]
    if len(report) == 0 or report_id not in existing_reports_id or report_id==5:
      return jsonify({'warning': 'there is not report with id: ' + str(report_id)})
    return jsonify({'report': report[0]})


if __name__ == '__main__':
    app.run()
