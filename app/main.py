import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    st.text("Generate personalized cold emails based on job postings.")

    # Input field
    url_input = st.text_input("Enter a URL:", value="https://www.uber.com/global/en/careers/list/134570/?utm_campaign=google_jobs_apply&utm_medium=organic&utm_source=google_jobs_apply")
    submit_button = st.button("Submit")

    if submit_button:
        if not url_input.strip():
            st.error("Please enter a valid URL.")
            return

        try:
            with st.spinner("Loading and processing the URL..."):
                # Load and clean data
                loader = WebBaseLoader([url_input])
                raw_data = loader.load()
                if not raw_data:
                    st.error("No content found at the provided URL.")
                    return
                data = clean_text(raw_data.pop().page_content)

                # Load portfolio and extract jobs
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)
                if not jobs:
                    st.warning("No job postings found in the provided URL.")
                    return

                # Generate emails for each job
                for idx, job in enumerate(jobs, start=1):
                    st.subheader(f"Job #{idx}: {job.get('role', 'Unknown Role')}")
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills) if skills else []
                    email = llm.write_mail(job, links)
                    st.code(email, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
