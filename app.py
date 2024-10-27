from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import subprocess
import os
import re
from lxml import etree
from celery import Celery
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'fallback_secret_key'  # Set secret key from .env

# Directory to store scan results
RESULTS_DIR = "scan_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'  # Redis as message broker
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Helper function to validate domain
def is_valid_domain(domain):
    regex = r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    return re.match(regex, domain)

# Celery task for scanning
@celery.task
def scan_domain_task(domain):
    if not is_valid_domain(domain):
        return {"error": "Invalid domain format."}

    result_xml = os.path.join(RESULTS_DIR, f"{domain}_nikto_scan.xml")
    result_html = os.path.join(RESULTS_DIR, f"{domain}_nikto_report.html")
    nikto_command = ['nikto', '-h', domain, '-o', result_xml, '-Format', 'xml']
    
    process = subprocess.Popen(nikto_command)
    process.wait()

    # Convert XML to HTML report
    xml_to_html_report(result_xml, result_html)
    
    return {"xml": os.path.basename(result_xml), "html": os.path.basename(result_html)}

# Function to convert XML report to HTML
def xml_to_html_report(xml_file, output_html):
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
        html = etree.Element("html")
        head = etree.SubElement(html, "head")
        title = etree.SubElement(head, "title")
        title.text = "Nikto Scan Report"

        body = etree.SubElement(html, "body")
        h1 = etree.SubElement(body, "h1")
        h1.text = "Nikto Scan Report"
        table = etree.SubElement(body, "table", border="1", cellspacing="0", cellpadding="5")
        header_row = etree.SubElement(table, "tr")
        headers = ["IP Address", "Vulnerability", "OSVDB ID"]

        for header in headers:
            th = etree.SubElement(header_row, "th")
            th.text = header

        for item in root.xpath("//scandetails/item"):
            row = etree.SubElement(table, "tr")
            ip = etree.SubElement(row, "td")
            ip.text = item.getparent().get("targetip")
            description = etree.SubElement(row, "td")
            description.text = item.findtext("description")
            osvdb_id = etree.SubElement(row, "td")
            osvdb_id.text = item.findtext("osvdbid")

        with open(output_html, "wb") as f:
            f.write(etree.tostring(html, pretty_print=True, method="html"))
    except Exception as e:
        print(f"Error creating HTML report: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        domain = request.form["domain"].strip()
        if domain:
            task = scan_domain_task.apply_async(args=[domain])  # Run scan asynchronously
            return jsonify({"task_id": task.id}), 202
        else:
            flash("Invalid domain format.", "error")
            return redirect(url_for("index"))
    return render_template("index.html")

@app.route("/status/<task_id>")
def task_status(task_id):
    task = scan_domain_task.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {"status": "Pending"}
    elif task.state == "SUCCESS":
        response = {"status": "Completed", "result": task.result}
    else:
        response = {"status": task.state}
    return jsonify(response)

# New API route to fetch scan results in JSON or file format
@app.route("/api/results/<domain>", methods=["GET"])
def api_get_scan_results(domain):
    result_xml = os.path.join(RESULTS_DIR, f"{domain}_nikto_scan.xml")
    result_html = os.path.join(RESULTS_DIR, f"{domain}_nikto_report.html")

    if os.path.exists(result_xml) and os.path.exists(result_html):
        return jsonify({
            "message": "Scan results found.",
            "xml_url": url_for("download_file", filename=f"{domain}_nikto_scan.xml", _external=True),
            "html_url": url_for("download_file", filename=f"{domain}_nikto_report.html", _external=True),
        })
    else:
        return jsonify({"error": "Scan results not found."}), 404

@app.route("/scan_results/<path:filename>")
def download_file(filename):
    # Check if file exists
    if os.path.exists(os.path.join(RESULTS_DIR, filename)):
        return send_from_directory(RESULTS_DIR, filename, as_attachment=True)
    else:
        return jsonify({"error": "File not found."}), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
