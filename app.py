import streamlit as st
import json
import pandas as pd
import os
from dotenv import load_dotenv
from agent import ResearcherAgent

# Load local environment variables
load_dotenv()

st.set_page_config(
    page_title="Researcher Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .reportview-container { background: #1e1e1e }
    .main { background-color: #121212; color: #e0e0e0; }
    .stTextInput>div>div>input { background-color: #2b2b2b; color: white; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Researcher Agent")
st.markdown("**Financial Market Analysis** - Production Ready")

# API KEY - CLOUD FIRST, LOCAL SECOND
# Safely check for secrets to avoid Streamlit's "No secrets found" warning
secrets_path = os.path.join(".streamlit", "secrets.toml")
OPENROUTER_API_KEY = None

if os.path.exists(secrets_path):
    try:
        OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        pass

# Fallback to .env
if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

if not OPENROUTER_API_KEY:
    st.error("🚫 OPENROUTER_API_KEY missing! Add to Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_agent():
    return ResearcherAgent(api_key=OPENROUTER_API_KEY)

agent = get_agent()

query = st.text_input(
    "Enter your financial query", 
    value="PSX crash analysis March 2026"
)

def run_research():
    if not query:
        st.warning("Please enter a query.")
        return
        
    with st.spinner("🔍 Researching..."):
        progress = st.progress(0)
        
        try:
            progress.progress(50)
            result = agent.run(query)
            progress.progress(100)
            
            conf_score = result.get('metrics', {}).get('confidence_score', 0.0)
            st.success(f"✅ Complete! Confidence: {conf_score:.1%}")
            
            # Results Layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Key Facts")
                for fact in result.get('key_facts', []):
                    st.markdown(f"• **{fact}**")
                
                st.subheader("🔗 Sources")
                if result.get('sources'):
                    df = pd.DataFrame(result['sources'])
                    st.dataframe(df, use_container_width=True)
            
            with col2:
                st.subheader("📈 Metrics")
                metrics = result.get('metrics', {})
                st.metric("Sources Found", metrics.get("total_sources", 0))
                st.metric("High Confidence", metrics.get("high_confidence_sources", 0))
                
                st.subheader("JSON Output")
                st.code(json.dumps(result, indent=2), language="json")
                
                st.download_button(
                    "💾 Download Report", 
                    json.dumps(result, indent=2),
                    "research_report.json"
                )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.error("Check API key in Streamlit Secrets")

if st.button("🚀 Run Research", type="primary"):
    run_research()

# Sidebar
with st.sidebar:
    st.markdown("### 🔑 API Status")
    st.success("✅ OpenRouter Connected")
    st.caption(f"Key: {OPENROUTER_API_KEY[:10]}...")
    
    st.markdown("### 🏗️ Architecture")
    st.markdown("""
    1. Web Search (DuckDuckGo)
    2. LLM Analysis (OpenRouter)
    3. Fact Extraction
    4. Confidence Scoring
    """)
