from flask import Flask, request, render_template_string, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = "/data"
PROCESSED_FOLDER = "/data/processed"
MAX_FILE_SIZE_MB = 5

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

HTML_FORM = """
<!doctype html>
<title>CSV Processor</title>
<h1>Upload CSV File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<hr>
<h2>Processed Files</h2>
<ul>
{% for file in files %}
  <li><a href="/download/{{ file }}">{{ file }}</a></li>
{% else %}
  <li>No processed files yet.</li>
{% endfor %}
</ul>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "No file uploaded.", 400
        if not file.filename.lower().endswith(".csv"):
            return "Invalid file type. Please upload a CSV.", 400
        file.seek(0, os.SEEK_END)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)
        if size_mb > MAX_FILE_SIZE_MB:
            return f"File too large. Max {MAX_FILE_SIZE_MB} MB allowed.", 400
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return f"✅ File '{file.filename}' uploaded successfully. Refresh to see processed results."

    processed_files = sorted(os.listdir(PROCESSED_FOLDER))
    return render_template_string(HTML_FORM, files=processed_files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)