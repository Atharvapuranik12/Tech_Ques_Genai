from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
import PyPDF2

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def post_process_text(text):
    cleaned_text = text.replace("**", "")
    return cleaned_text


def generate_custom_tech_questions(skills):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    prompt = (f"""can you give me 10 interview questions for freshers based on the mandatory skills mentioned 
    the job description as follows {skills} 
    I need response in a structure as
        [
            {{
                "question_id": 1,
                "response": ""
            }},
            ...
        ]
    """)
    response = model.generate_content(prompt)
    return post_process_text(response.text)


def generate_custom_non_tech_questions(resume_text, job_description_text):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    prompt = (f"""Imagine you are conducting an interview with a candidate who has submitted a resume highlighting their 
              work experience and projects relevant to the position. Craft a set of questions that delve into their 
              past experiences and assess their technical skills based on the requirements outlined in the job 
              description. Work Experience: Review the candidate's work experience as outlined in their resume. 
              Craft questions that explore specific accomplishments, challenges faced, and roles undertaken in their 
              previous positions. Project Experience: Analyze the projects listed on the candidate's resume. Develop 
              questions that probe into the methodologies employed, the candidate's contributions, problem-solving 
              strategies, and lessons learned from these projects. Technical Skills: Referencing the technical 
              skills mentioned in the job description, devise questions to evaluate the candidate's proficiency in 
              these areas. These questions should assess not only theoretical knowledge but also practical 
              application and problem-solving abilities. Integration of Experience and Skills: Formulate questions 
              that require the candidate to integrate their past work experiences and technical skills. This could 
              involve hypothetical scenarios or real-world challenges relevant to the role they are applying for
              here is the resume \n{resume_text} \n\n here is the job description \n{job_description_text} 
              I need response in a structure as
                    [
                        {{
                            "question_id": 1,
                            "response": ""
                        }},
                        ...
                    ]
              """)

    response = model.generate_content(prompt)
    return post_process_text(response.text)


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    resume_file = request.files['resume']
    job_description_file = request.files['job_description']

    resume_text = extract_text_from_pdf(resume_file)
    job_description_text = extract_text_from_pdf(job_description_file)
    skills = "Node.js, React.js, AWS, JavaScript"

    custom_ntquestions = generate_custom_non_tech_questions(resume_text, job_description_text)
    custom_tquestions = generate_custom_tech_questions(skills)
    return render_template('result.html', custom_questions=custom_ntquestions + "\n\n" + custom_tquestions)


if __name__ == '__main__':
    app.run(debug=True)
