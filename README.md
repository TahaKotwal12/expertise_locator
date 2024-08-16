# Expertise Locator

## Overview

Expertise Locator is a web-based application that allows organizations to efficiently search for colleagues with specific expertise based on their resumes. This tool facilitates knowledge sharing and mentoring opportunities by providing a centralized system for storing and searching employee skills and experiences.

## Features

- Upload and process PDF and DOCX resumes
- Extract text content from resumes
- Vectorize resume content for efficient searching
- Store resume data and vectors in a TiDB database
- Search for expertise using natural language queries
- Display matching employees based on similarity scores

## Technologies Used

- Python 3.7+
- Flask (Web Framework)
- PyPDF2 (PDF parsing)
- python-docx (DOCX parsing)
- scikit-learn (TF-IDF Vectorization and Cosine Similarity)
- PyMySQL (Database connection)
- TiDB (Database)

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Access to a TiDB database
- SSL certificate for TiDB connection (isrgrootx1.pem)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/expertise-locator.git
   cd expertise-locator
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install flask PyPDF2 python-docx scikit-learn pymysql numpy
   ```

5. Place your `isrgrootx1.pem` SSL certificate in the project root directory.

6. Update the TiDB connection details in `app.py`:
   ```python
   connection = pymysql.connect(
       host='your_tidb_host',
       user='your_username',
       password='your_password',
       database='your_database',
       port=4000,
       ssl=ssl_context
   )
   ```

## Usage

1. Start the Flask application:
   ```
   flask run
   ```

2. Open a web browser and navigate to `http://localhost:5000`.

3. Upload resumes:
   - Click on the "Choose File" button in the "Upload Resume" section.
   - Select a PDF or DOCX file.
   - Click "Upload" to process and store the resume.

4. Search for expertise:
   - Enter skills or expertise in the search box.
   - Click "Search" to find matching employees.
   - View the results, which show employee names and similarity scores.

## Project Structure

```
expertise_locator/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── uploads/
├── isrgrootx1.pem
├── requirements.txt
└── README.md
```

## Customization

- To modify the UI, edit the HTML (`templates/index.html`) and CSS (`static/style.css`) files.
- To change the vectorization method or similarity calculation, update the relevant functions in `app.py`.
- To add more features or modify the database schema, update the SQL queries and table structures in `app.py`.







