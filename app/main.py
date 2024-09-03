import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import time

def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="URL2Email", page_icon="👨🏻‍💻")
    st.title("👨🏻‍💻URL2Email")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url_input = st.text_input("Enter a URL:", placeholder="https://example.com/job-posting")
    
    with col2:
        submit_button = st.button("Submit", type="primary")

    if submit_button:
        with st.spinner('Processing...'):
            retry_attempts = 3
            for attempt in range(retry_attempts):
                try:
                    loader = WebBaseLoader([url_input])
                    data = clean_text(loader.load().pop().page_content)
                    
                    portfolio_progress = st.progress(0)
                    portfolio.load_portfolio()
                    portfolio_progress.progress(50)
                    
                    jobs = llm.extract_jobs(data)
                    portfolio_progress.progress(75)
                    
                    for job in jobs:
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        email = llm.write_mail(job, links)
                        st.code(email, language='markdown')
                    
                    portfolio_progress.progress(100)
                    break  # Break if successful

                except Exception as e:
                    if '503' in str(e):
                        st.warning(f"Attempt {attempt + 1} of {retry_attempts}: Service Unavailable. Retrying in 5 seconds...")
                        time.sleep(5)
                    else:
                        st.error(f"An Error Occurred: {e}. Please make sure the URL is correct and accessible.")
                        break
            else:
                st.error("Failed to retrieve data after multiple attempts. Please try again later.")

# Main script execution
if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)