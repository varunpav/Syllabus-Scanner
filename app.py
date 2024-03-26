from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import spacy
import fitz  # PyMuPDF
from docx import Document


# Initialize Flask app
app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_dates(text):
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    return dates

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        process_file(file_path)
        return jsonify({'message': 'File uploaded and processed successfully'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    if not request.data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = request.data.decode('utf-8')
    dates = extract_dates(text)
    
    return jsonify({'dates': dates}), 200

def process_file(file_path):
    if file_path.endswith('.pdf'):
        text = ''
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        with open(file_path, 'r') as file:
            text = file.read()
    return extract_dates(text)

if __name__ == '__main__':
    app.run(debug=True)


