# Import necessary libraries
from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import docx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
import ssl
from werkzeug.utils import secure_filename
import pickle

# Initialize Flask application
app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global vectorizer object
vectorizer = None

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def connect_to_tidb():
    """
    Establish a secure connection to TiDB database
    """
    ssl_context = ssl.create_default_context(cafile="isrgrootx1.pem")
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = True

    connection = pymysql.connect(
        host='gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
        user='2AfUjtxfS59xS5Y.root',
        password='uiViII7wrPJ8TNkg',
        database='fortune500',
        port=4000,
        ssl=ssl_context
    )
    return connection

def create_employees_table(connection):
    """
    Create the 'employees' table if it doesn't exist
    """
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            resume_text TEXT,
            resume_vector BLOB
        )
        """)
    connection.commit()

def create_vectorizer_table(connection):
    """
    Create the 'vectorizer' table if it doesn't exist
    """
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vectorizer (
            id INT PRIMARY KEY,
            vectorizer BLOB
        )
        """)
    connection.commit()

def upsert_vectorizer(connection, vectorizer):
    """
    Insert or update the vectorizer in the database
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "REPLACE INTO vectorizer (id, vectorizer) VALUES (%s, %s)",
            (1, pickle.dumps(vectorizer))
        )
    connection.commit()

def get_vectorizer(connection):
    """
    Retrieve the vectorizer from the database or create a new one if it doesn't exist
    """
    global vectorizer
    if vectorizer is None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT vectorizer FROM vectorizer WHERE id = 1")
            result = cursor.fetchone()
            if result:
                vectorizer = pickle.loads(result[0])
            else:
                vectorizer = TfidfVectorizer()
    return vectorizer

def insert_employee(connection, name, resume_text, resume_vector):
    """
    Insert a new employee record into the database
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO employees (name, resume_text, resume_vector) VALUES (%s, %s, %s)",
            (name, resume_text, resume_vector.tobytes())
        )
    connection.commit()

def read_pdf(file_path):
    """
    Extract text content from a PDF file
    """
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def read_docx(file_path):
    """
    Extract text content from a DOCX file
    """
    doc = docx.Document(file_path)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])

@app.route('/')
def index():
    """
    Render the main page of the application
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    """
    Handle resume upload, process the file, and store the data
    """
    global vectorizer
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file and allowed_file(file.filename):
        try:
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract text from the file
            if file.filename.endswith('.pdf'):
                text = read_pdf(file_path)
            else:
                text = read_docx(file_path)

            # Connect to the database and create necessary tables
            connection = connect_to_tidb()
            create_employees_table(connection)
            create_vectorizer_table(connection)

            # Get or create the vectorizer and fit it with the new text
            vectorizer = get_vectorizer(connection)
            vectorizer.fit([text])
            upsert_vectorizer(connection, vectorizer)
            
            # Transform the text into a vector
            vector = vectorizer.transform([text]).toarray()[0]
            name = os.path.splitext(filename)[0]

            # Insert the employee data into the database
            insert_employee(connection, name, text, vector)
            connection.close()

            # Remove the temporary file
            os.remove(file_path)

            return jsonify({'success': 'Resume uploaded and processed successfully'})
        except Exception as e:
            app.logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Allowed file types are pdf and docx'}), 400

@app.route('/search', methods=['POST'])
def search_expertise():
    """
    Search for expertise based on the input query
    """
    global vectorizer
    query = request.json['query']
    
    # Connect to the database and get the vectorizer
    connection = connect_to_tidb()
    vectorizer = get_vectorizer(connection)
    
    if vectorizer is None:
        return jsonify({'error': 'No resumes have been uploaded yet'}), 400
    
    # Transform the query into a vector
    query_vector = vectorizer.transform([query]).toarray()[0]

    # Fetch all employee vectors from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, resume_vector FROM employees")
        employees = cursor.fetchall()

    # Calculate similarity scores
    results = []
    for emp_id, name, resume_vector in employees:
        emp_vector = np.frombuffer(resume_vector, dtype=np.float64)
        if emp_vector.shape[0] != query_vector.shape[0]:
            app.logger.warning(f"Incompatible vector dimensions for employee {name}. Skipping.")
            continue
        similarity = cosine_similarity([query_vector], [emp_vector])[0][0]
        results.append({'id': emp_id, 'name': name, 'similarity': float(similarity)})

    # Sort results by similarity score
    results.sort(key=lambda x: x['similarity'], reverse=True)
    connection.close()
    return jsonify(results[:5])  # Return top 5 matches

if __name__ == '__main__':
    app.run(debug=True)