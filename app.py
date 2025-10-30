import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
import os
import re

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from neo4j_helper import Neo4jHelper
from ai_helper import AIHelper
from excel_processor import ExcelProcessor

# Page configuration
st.set_page_config(
    page_title="Employee Intelligence Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom CSS for styling ----
st.markdown("""
<style>
    .main-header-container { text-align: center; padding-top: 10px; padding-bottom: 5px; }
    .main-header {
        font-size: 3.5rem; font-weight: 800; color: #FFFFFF;
        text-shadow: 0 0 10px rgba(255,255,255,0.4);
    }
    .main-subheader { font-size: 1.25rem; color: #B0B0B0; margin-top: -0.5rem; }
    
    /* Cypher Query Styling */
    .cypher-section {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .cypher-title {
        color: #007bff;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .records-count {
        background-color: #e9ecef;
        padding: 8px 12px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9em;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---- Session State Initialization ----
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "neo4j_uri" not in st.session_state:
        st.session_state.neo4j_uri = "neo4j+s://.databases.neo4j.io"
    if "neo4j_username" not in st.session_state:
        st.session_state.neo4j_username = "neo4j"
    if "neo4j_password" not in st.session_state:
        st.session_state.neo4j_password = "Password123!"
    if "api_key" not in st.session_state:
        # st.session_state.api_key = "AI***********************************mCM"
        st.session_state.api_key = "AIzaSy**************************************oAM"
    if "model_name" not in st.session_state:
        st.session_state.model_name = "gemini-2.0-flash-exp"
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "Google Gemini"
    if "neo4j_connected" not in st.session_state:
        st.session_state.neo4j_connected = False
    if "ai_configured" not in st.session_state:
        st.session_state.ai_configured = False
    if "database_initialized" not in st.session_state:
        st.session_state.database_initialized = False

initialize_session_state()

# ---- Connection Tests ----
def test_connections(api_key, neo4j_uri, username, password):
    results = []
    try:
        neo4j_helper = Neo4jHelper(neo4j_uri, username, password)
        if neo4j_helper.test_connection():
            st.session_state.neo4j_connected = True
            results.append("✅ Neo4j connection successful!")
        else:
            st.session_state.neo4j_connected = False
            results.append("❌ Neo4j connection failed!")
    except Exception as e:
        st.session_state.neo4j_connected = False
        results.append(f"❌ Neo4j connection error: {str(e)}")

    if api_key:
        try:
            ai_helper = AIHelper(api_key, st.session_state.model_name, st.session_state.llm_provider)
            if ai_helper.test_connection():
                st.session_state.ai_configured = True
                results.append("✅ AI API connection successful!")
            else:
                st.session_state.ai_configured = False
                results.append("❌ AI API connection failed!")
        except Exception as e:
            st.session_state.ai_configured = False
            results.append(f"❌ AI API connection error: {str(e)}")
    else:
        results.append("⚠️ AI API key not provided")

    for result in results:
        if "✅" in result:
            st.success(result)
        elif "❌" in result:
            st.error(result)
        else:
            st.warning(result)

# ---- Database Initialization ----
def initialize_database(uploaded_file, uri, username, password):
    try:
        with st.spinner("🔄 Initializing database..."):
            excel_processor = ExcelProcessor()
            success = excel_processor.import_excel_to_neo4j(uploaded_file, uri, username, password)
            if success:
                st.session_state.database_initialized = True
                st.success("✅ Database initialized successfully!")
                neo4j_helper = Neo4jHelper(uri, username, password)
                summary = neo4j_helper.get_database_summary()
                st.subheader("📊 Import Summary")
                for label, count in summary.items():
                    st.write(f"**{label}:** {count}")
            else:
                st.error("❌ Database initialization failed!")
    except Exception as e:
        st.error(f"❌ Error initializing database: {str(e)}")

# ---- Query Processor ----
def process_user_query(question, api_key, model, provider, neo4j_uri, username, password):
    st.session_state.chat_history.append({"role": "user", "content": question})
    if not api_key or not neo4j_uri:
        msg = "⚠️ Please configure both API key and database connection first."
        st.session_state.chat_history.append({"role": "assistant", "content": msg})
        st.error(msg)
        return

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                ai_helper = AIHelper(api_key, model, provider)
                neo4j_helper = Neo4jHelper(neo4j_uri, username, password)

                cypher_generation = ai_helper.generate_cypher_query(question)
                print(f"Generated Cypher query: {cypher_generation}")
                if not cypher_generation.get("success"):
                    error_msg = cypher_generation.get("error", "Could not understand your question.")
                    st.error(f"❌ {error_msg}")
                    
                    # Show that no Cypher query was executed due to error
                    st.markdown("---")
                    st.markdown("""
                    <div class="cypher-section">
                        <div class="cypher-title">🔍 Executed Cypher Query:</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.error("❌ No Cypher query executed - error in query generation")
                    
                    full_response = f"❌ {error_msg}\n\n---\n\n**🔍 Executed Cypher Query:**\n❌ No Cypher query executed - error in query generation"
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    return

                # Handle smalltalk or non-database queries gracefully
                if cypher_generation.get("response_type") in ["smalltalk", "error"]:
                    msg = cypher_generation.get("message", "Hello! How can I help you?")
                    st.markdown(msg)
                    
                    # Show that no Cypher query was executed for smalltalk/error responses
                    st.markdown("---")
                    st.markdown("""
                    <div class="cypher-section">
                        <div class="cypher-title">🔍 Executed Cypher Query:</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info("ℹ️ No Cypher query executed - this was a conversational response")
                    
                    full_response = f"{msg}\n\n---\n\n**🔍 Executed Cypher Query:**\nℹ️ No Cypher query executed - this was a conversational response"
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    return

                cypher_query = cypher_generation["cypher_query"]
                query_type = cypher_generation.get("query_type", "search")

                query_result = neo4j_helper.execute_query(cypher_query)
                print(f"Executed Cypher query result: {query_result}")

                if not query_result["success"]:
                    st.error(f"❌ Database query failed: {query_result['error']}")
                    
                    # Show the Cypher query that failed
                    st.markdown("---")
                    st.markdown("""
                    <div class="cypher-section">
                        <div class="cypher-title">🔍 Executed Cypher Query:</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(cypher_query, language="cypher")
                    st.error(f"❌ **Query Failed:** {query_result['error']}")
                    
                    full_response = f"❌ Database query failed: {query_result['error']}\n\n---\n\n**🔍 Executed Cypher Query:**\n```cypher\n{cypher_query}\n```\n\n❌ **Query Failed:** {query_result['error']}"
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    return

                data = query_result["data"]

                response = ai_helper.generate_sophisticated_response(question, data, query_type, cypher_query)
                print(f"AI Response: {response}")

                if not response["success"]:
                    response_text = format_basic_response(data, question, query_type)
                else:
                    response_text = response["answer"]

                st.markdown(response_text)

                # Always show the Cypher query that was executed with enhanced styling
                st.markdown("---")
                st.markdown("""
                <div class="cypher-section">
                    <div class="cypher-title">🔍 Executed Cypher Query:</div>
                </div>
                """, unsafe_allow_html=True)
                st.code(cypher_query, language="cypher")
                st.markdown(f"""
                <div class="records-count">📊 Records Found: {len(data)}</div>
                """, unsafe_allow_html=True)
                
                # Add a copy button for the query
                if st.button("📋 Copy Query", key=f"copy_{len(st.session_state.chat_history)}"):
                    st.code(cypher_query, language="cypher")
                    st.success("Query copied! (You can copy from the code block above)")

                # Combine response with query for chat history
                full_response = f"{response_text}\n\n---\n\n**🔍 Executed Cypher Query:**\n```cypher\n{cypher_query}\n```\n\n**📊 Records Found:** {len(data)}"
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"❌ Error processing question: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": str(e)})

# ---- Basic Fallback Response ----
def format_basic_response(data, question, query_type):
    if not data:
        return "🤷 I couldn't find any data matching your query."
    count = len(data)
    print(f"Basic response data count: {count}")
    if query_type == "count":
        return f"📊 I found {count} results."
    elif query_type == "list":
        return f"📋 Here are {count} items I found:"
    else:
        return f"✅ I found {count} matching records."

# ---- Chat Interface ----
def render_chat_interface(api_key, model, provider, neo4j_uri, username, password):
    st.markdown("<p style='text-align:center;'>Ask about employees, skills, projects, or structure.</p>", unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about employees, skills, or projects..."):
        process_user_query(prompt, api_key, model, provider, neo4j_uri, username, password)
        st.rerun()

# ---- Sidebar ----
with st.sidebar:
    st.subheader("⚙️ AI Settings")
    provider = st.selectbox("Provider", ["Google Gemini", "OpenAI"], key="llm_provider")
    model = st.text_input("Model", value=st.session_state.model_name, key="model_name")
    api_key = st.text_input("API Key", type="password", value=st.session_state.api_key, key="api_key_input")

    st.subheader("🗄️ Database")
    neo4j_uri = st.text_input("URI", value=st.session_state.neo4j_uri, key="neo4j_uri_input")
    neo4j_username = st.text_input("Username", value=st.session_state.neo4j_username, key="neo4j_username_input")
    neo4j_password = st.text_input("Password", type="password", value=st.session_state.neo4j_password, key="neo4j_password_input")

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file and st.button("🚀 Initialize Database", use_container_width=True):
        initialize_database(uploaded_file, neo4j_uri, neo4j_username, neo4j_password)

    if st.button("🧪 Test Connections", use_container_width=True):
        test_connections(api_key, neo4j_uri, neo4j_username, neo4j_password)
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ---- Main Page ----
st.markdown("""
<div class="main-header-container">
    <div class="main-header">LogicMind</div>
    <div class="main-subheader">🤖 Employee Intelligence Assistant 🤖</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

render_chat_interface(
    st.session_state.api_key,
    st.session_state.model_name,
    st.session_state.llm_provider,
    st.session_state.neo4j_uri,
    st.session_state.neo4j_username,
    st.session_state.neo4j_password
)

if __name__ == "__main__":
    pass
