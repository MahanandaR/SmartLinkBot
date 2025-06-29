import streamlit as st
from rag import generate_answer, process_urls
import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

# Page config
st.set_page_config(page_title="Smart URL Answer Bot", page_icon="🔗", layout="centered")

# Dark Mode Toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

# Custom CSS
st.markdown(
    f"""
    <style>
    html, body, [data-testid="stApp"]  {{
        background-color: {"#1e1e1e" if dark_mode else "#ffffff"};
        color: {"#f5f5f5" if dark_mode else "#000000"};
    }}
     section[data-testid="stSidebar"] * {{
        color: {"white" if dark_mode else "black"} !important;
    }}

    /* Ensure toggle label is visible */
    section[data-testid="stSidebar"] label[data-testid="stToggleLabel"] {{
        color: {"white" if dark_mode else "black"} !important;
        font-weight: bold;
    }}

    .main .block-container {{
        max-width: 100% !important;
        padding: 1rem 1rem;
    }}
    
    .header-container {{
        background-color: {"#4a148c" if dark_mode else "#800080"};
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        width: 100%;
        color: white;
   
    }}

    .stTextInput>div>div>input {{
        border: 2px solid #800080 !important;
        border-radius: 8px !important;
        background-color: {"#2c2c2c" if dark_mode else "#f9f9f9"} !important;
        padding: 10px;
        width: 100% !important;
        color: {"white" if dark_mode else "black"};

        }}

        
        /* Fix sidebar background and text color */
    section[data-testid="stSidebar"] {{
        background-color: {"#2c2c2c" if dark_mode else "#f0f2f6"} !important;
        color: {"#f5f5f5" if dark_mode else "#000000"} !important;
    }}
    

    .stButton>button {{
        background-color: #800080 !important;
        color: white !important;
        border-radius: 8px !important;
        height: 3em;
        width: 100%;
        border: none;
        
    }}

    .answer-card {{
        background-color: {"#2b2b2b" if dark_mode else "#f5f5f5"};
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #800080;
        color: {"#ffffff" if dark_mode else "#000000"};
        background-color: {"#1e1e1e" if dark_mode else "#ffffff"};
        
    }}

    .question-input-wrapper {{
        position: sticky;
        bottom: 0;
        background-color: {"#1e1e1e" if dark_mode else "#ffffff"};
        padding: 10px 0;
        color: {"#f5f5f5" if dark_mode else "#000000"};
    }}

    .markdown-text-container {{
        color: {"#dddddd" if dark_mode else "#000000"} !important;
        background-color: {"#1e1e1e" if dark_mode else "#ffffff"};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown("""
    <div class="header-container">
        <h1><img src="https://img.icons8.com/?size=100&id=IEDjCJWFqQAs&format=png&color=FFFFFF" width="40"> SmartLinkBot</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("Ask questions based on content from your favorite web pages.")

# Sidebar URL inputs
st.sidebar.header("🌐 Enter URLs to Process")
url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

status_placeholder = st.empty()

# Process Button
if st.sidebar.button("🚀 Process URLs"):
    urls = [u for u in [url1, url2, url3] if u.strip()]
    if not urls:
        status_placeholder.error("⚠️ Please enter at least one valid URL.")
    else:
        for status in process_urls(urls):
            status_placeholder.info(status)


st.markdown("---")

# Ask Question
st.subheader("💬 Ask a Question")
st.markdown("<div class='question-input-wrapper'>", unsafe_allow_html=True)
query = st.text_input("Type your question here and press Enter:")
st.markdown("</div>", unsafe_allow_html=True)

if query:
    try:
        with st.spinner("⏳ Generating your answer..."):
            answer, sources = generate_answer(query)

        st.markdown("### 🧠 Answer")
        st.markdown(f"<div class='answer-card'>{answer}</div>", unsafe_allow_html=True)

        if sources:
            st.markdown("### 📚 Sources")
            for src in sources.strip().split("\n"):
                if src.strip():
                    st.markdown(f"- {sources}")

    except RuntimeError:
        st.error("⚠️ You must process the URLs first before asking a question.")
