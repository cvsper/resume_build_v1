#!/usr/bin/env python3
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>Create First Buttons Test</h1>
    <p><a href="/test_resumes_empty">Test Resumes (Empty)</a></p>
    <p><a href="/test_resumes_with_data">Test Resumes (With Data)</a></p>
    <p><a href="/test_cover_letters_empty">Test Cover Letters (Empty)</a></p>
    <p><a href="/test_cover_letters_with_data">Test Cover Letters (With Data)</a></p>
    <p><a href="/test_interview_qa_empty">Test Interview Q&A (Empty)</a></p>
    <p><a href="/test_interview_qa_with_data">Test Interview Q&A (With Data)</a></p>
    '''

@app.route('/test_resumes_empty')
def test_resumes_empty():
    return render_template('resumes.html', resumes=[])

@app.route('/test_resumes_with_data')
def test_resumes_with_data():
    sample_resumes = [
        {'id': 1, 'filename': 'resume1.pdf', 'created_at': '2024-01-01'},
        {'id': 2, 'filename': 'resume2.pdf', 'created_at': '2024-01-02'}
    ]
    return render_template('resumes.html', resumes=sample_resumes)

@app.route('/test_cover_letters_empty')
def test_cover_letters_empty():
    return render_template('cover_letters.html', cover_letters=[])

@app.route('/test_cover_letters_with_data')
def test_cover_letters_with_data():
    sample_cover_letters = [
        {'id': 1, 'filename': 'cover_letter1.pdf', 'created_at': '2024-01-01'},
        {'id': 2, 'filename': 'cover_letter2.pdf', 'created_at': '2024-01-02'}
    ]
    return render_template('cover_letters.html', cover_letters=sample_cover_letters)

@app.route('/test_interview_qa_empty')
def test_interview_qa_empty():
    return render_template('interview_qa.html', interview_qa_list=[])

@app.route('/test_interview_qa_with_data')
def test_interview_qa_with_data():
    sample_qa = [
        {'id': 1, 'filename': 'qa1.pdf', 'created_at': '2024-01-01'},
        {'id': 2, 'filename': 'qa2.pdf', 'created_at': '2024-01-02'}
    ]
    return render_template('interview_qa.html', interview_qa_list=sample_qa)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
