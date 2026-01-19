import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper

# 1. Page Configuration
st.set_page_config(page_title="Universal Sustainability Auditor", layout="wide")

# --- NEW: WELCOME DIALOG ---
@st.dialog("🚀 Welcome to the Universal Auditor")
def show_welcome():
    st.markdown("""
    ### Quick Start Guide:
    1. **🔑 Configure:** Enter your Gemini API Key in the sidebar.
    2. **📤 Upload:** Provide a Sustainability Report PDF in Tab 1.
    3. **🔍 Search:** Get the latest & historical industry trends in Tab 2.
    4. **⚖️ Audit:** Run the deep-dive analysis and download your report.
    5. **💬 Chat:** Ask the AI specific questions about the data.
    """)
    if st.button("Start Auditing"):
        st.session_state.welcome_shown = True
        st.rerun()

# Trigger welcome popup on first load
if "welcome_shown" not in st.session_state:
    show_welcome()

# 2. Sidebar for API Key
with st.sidebar:
    st.title("🔑 Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("Gemini Brain Active!")

st.title("🌱 Universal Sustainability Auditor")
st.markdown("---")

# 3. Setup Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload & Extract", 
    "🔍 Trend Benchmarking", 
    "⚖️ Superior Audit", 
    "💬 Chat with Report"
])

# --- TAB 1: UPLOAD & EXTRACT ---
with tab1:
    st.header("Upload Sustainability Report")
    uploaded_file = st.file_uploader("Choose any Sustainability PDF", type="pdf")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        st.session_state['report_text'] = text
        st.success("Data Extracted Successfully!")
        st.text_area("Preview extracted text:", text[:1000] + "...", height=200)

# --- TAB 2: TREND BENCHMARKING (HISTORICAL + FUTURE) ---
with tab2:
    st.header("Industry Evolution & Benchmarks")
    industry = st.text_input("Enter Industry (e.g., On-Demand Tech, Aviation, Banking)")
    
    if st.button("Search Past, Present & Future Standards"):
        if industry:
            with st.spinner(f"Analyzing {industry} trends..."):
                search = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper())
                # Optimized for historical context + recent updates
                query = f"Evolution of sustainability standards, recent ESG benchmarks, and upcoming 2026-2030 targets for {industry}"
                results = search.run(query)
                st.session_state['benchmarks'] = results
                st.write("### Found Industry Context:")
                st.write(results)
        else:
            st.warning("Please enter an industry name.")

# --- TAB 3: THE SUPERIOR AUDIT ---
with tab3:
    st.header("Deep Dive Audit")
    if st.button("Run Superior Audit"):
        if 'report_text' in st.session_state and 'benchmarks' in st.session_state:
            with st.spinner("Gemini 3 is performing a comparative audit..."):
                model = genai.GenerativeModel('gemini-3-flash-preview')
                
                audit_prompt = f"""
                You are a Senior ESG Analyst. Perform a comparative audit of this report.
                1. HISTORICAL CONTEXT: How do their current results compare to recent industry benchmarks?
                2. FORWARD-LOOKING: Are they prepared for upcoming 2026-2030 regulatory shifts?
                3. TREND ANALYSIS: Is their progress accelerating, or is it stagnant?
                4. AUTHENTICITY: Identify if claims match the historical data trends for {industry}.
                
                REPORT DATA: {st.session_state['report_text'][:30000]}
                BENCHMARKS & TRENDS: {st.session_state['benchmarks']}
                """
                
                response = model.generate_content(audit_prompt)
                st.session_state['audit_result'] = response.text
                st.markdown("### ⚖️ Final Audit Result")
                st.write(response.text)
        else:
            st.error("Error: Please complete Tab 1 and Tab 2 first!")

    # DOWNLOAD BUTTON (Visible only after audit is run)
    if 'audit_result' in st.session_state:
        st.divider()
        st.download_button(
            label="📥 Download Audit Report (.txt)",
            data=st.session_state['audit_result'],
            file_name="Sustainability_Audit_Report.txt",
            mime="text/plain"
        )

# --- TAB 4: Q&A CHAT (50,000 CHAR CAPACITY) ---
with tab4:
    st.header("💬 Chat with your Report")
    st.info("Ask specific questions about data points, targets, or mentions of past performance.")
    
    user_question = st.text_input("Enter your question:")
    
    if user_question:
        if 'report_text' in st.session_state:
            with st.spinner("Searching the report..."):
                model = genai.GenerativeModel('gemini-3-flash-preview')
                
                qa_prompt = f"""
                You are a sustainability expert. Use the following report text to answer the question.
                Reference specific data, dates, or figures found in the text.
                
                Report Text: {st.session_state['report_text'][:50000]} 
                
                Question: {user_question}
                """
                
                response = model.generate_content(qa_prompt)
                st.markdown("### Answer:")
                st.write(response.text)
        else:
            st.error("Please upload the PDF in Tab 1 first!")