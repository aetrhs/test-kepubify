from flask import Flask, request, send_file, render_template, abort
import os
import subprocess
import uuid

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'.epub'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for uploaded files (simulating DB)
uploaded_files = []

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append({'id': filename, 'name': file.filename})
            return render_template('index.html', files=uploaded_files, message='File uploaded successfully')
        return 'Invalid file type. Only EPUB allowed.', 400
    return render_template('index.html', files=uploaded_files)

@app.route('/download/<file_id>')
def download_file(file_id):
  file_data = next((f for f in uploaded_files if f['id'] == file_id), None)
  if not file_data:
    abort(404)
  
  input_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
  output_path = input_path + '.kepub.epub'
  
  try:
    print(f"Running kepubify: bin\\kepubify -v {input_path}")
    result = subprocess.run(
      ['bin/kepubify', '-v', input_path],
      check=True,
      capture_output=True,
      text=True,
      cwd=os.path.dirname(os.path.abspath(__file__))
    )
    print(f"Kepubify stdout: {result.stdout}\nStderr: {result.stderr}")

    print(f"Files in bin: {os.listdir('bin')}")
    print(f"Current dir: {os.getcwd()}")
    print(f"Running kepubify: bin/kepubify -v {input_path}")

    if os.path.exists(output_path):
      response = send_file(
        output_path,
        as_attachment=True,
        download_name=f"{os.path.splitext(file_data['name'])[0]}.kepub.epub",
        mimetype='application/epub+zip'
      )
      os.remove(output_path)  # Cleanup
      return response
    else:
      return f"Output file not found: {output_path}", 500
  except subprocess.CalledProcessError as e:
    error_msg = f"Conversion failed: Return code {e.returncode}\nStdout: {e.stdout}\nStderr: {e.stderr}"
    print(error_msg)
    return error_msg, 500
  except FileNotFoundError:
    return 'kepubify not found. Ensure bin/kepubify exists.', 500

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)