from __future__ import annotations

import streamlit as st
from PyPDF2 import PdfReader
from gpt import get_gpt_response


def extract_resume_data(data: str, job_descr: str, key: str) -> dict | None:
    gpt_response = get_gpt_response(data, job_descr, key)
    response_message = gpt_response["choices"][0]["message"]
    reviews = response_message.get("function_call")
    result = reviews.get("arguments")
    if reviews and isinstance(result, dict):
        return result

    if reviews and isinstance(result, str):
        import json
        try:
            json_result = json.loads(result)
            return json_result
        except json.JSONDecodeError as e:
            print("Error: Cannot be convert to a JSON object.")
            print(e)
    return None


# ---------------------------------
st.set_page_config(page_title='📝 Resume Ratings', page_icon="📝")
st.title("📝 Resume Ratings")
st.markdown("Use this application to help you decide if the prospect is a good fit for the job.")

with st.form(key='resume_form'):
    job_description = st.text_area(label="""Write the Job Description here.
                                            Insert key aspects you want to value in the prospect's resume.""",
                                   placeholder="Job description. This field should have at least 100 characters.")
    file = st.file_uploader("Add the prospect's resume in PDF format:", type=["pdf"])
    openai_api_key = st.text_input('OpenAI API Key', type='password', disabled=not (job_description, file),
                                   help="Insert the job description and file first. Then add the OpenAI API key here.")
    submitted = st.form_submit_button('Submit', disabled=not (job_description, file, openai_api_key))

if file is not None and len(job_description) > 100:
    pdf_file = PdfReader(file)
    pdf_text = ""
    for page in pdf_file.pages:
        pdf_text += page.extract_text() + "\n"

    resume_data = extract_resume_data(pdf_text, job_description, openai_api_key)
    if resume_data:
        education = int(resume_data.get("education", 0))
        company_fit = int(resume_data.get("company_fit", 0))
        technical_skills = int(resume_data.get("technical_skills", 0))
        soft_skills = int(resume_data.get("soft_skills", 0))
        projects = int(resume_data.get("projects", 0))
        average = (education + company_fit + technical_skills + soft_skills + projects) // 5

        st.title("Prospect Review Based On Job Description")
        st.markdown(f"### Name: {resume_data.get('name')}")
        st.markdown(f"#### Relevant skills:\n{resume_data.get('relevant_skills')}")
        st.markdown(f"#### Summary:\n{resume_data.get('summary')}")
        st.slider(
            label="Years of experience",
            min_value=1,
            max_value=15,
            value=int(resume_data.get('years_of_experience')),
            disabled=True)
        st.slider(
            label="Education",
            min_value=1,
            max_value=10,
            value=education,
            disabled=True
        )
        st.slider(
            label="Company fit",
            min_value=1,
            max_value=10,
            value=company_fit,
            disabled=True
        )
        st.slider(
            label="Technical Skills",
            min_value=1,
            max_value=10,
            value=technical_skills,
            disabled=True
        )
        st.slider(
            label="Soft Skills",
            min_value=1,
            max_value=10,
            value=soft_skills,
            disabled=True
        )
        st.slider(
            label="Projects",
            min_value=1,
            max_value=10,
            value=projects,
            disabled=True
        )
        st.markdown("### Average Score")
        st.slider(
            label="",
            min_value=1,
            max_value=10,
            value=average,
            disabled=True
        )

