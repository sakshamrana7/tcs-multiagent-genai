"""
Streamlit Web UI for TCS Multi-Agent GenAI Tool
Simple structured data interface with RAG
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.database import (
    init_database,
    seed_sample_data,
    get_customer_profile,
    get_customer_support_tickets,
    search_customers,
)
from backend.rag.rag_pipeline import (
    search_documents,
    seed_sample_documents,
    get_collection_info,
    add_documents,
)
from backend.chatbot import generate_answer

# Page config
st.set_page_config(page_title="TCS GenAI", page_icon="🤖", layout="wide")

# Title
st.markdown("# 🤖 TCS Multi-Agent GenAI")
st.markdown("Customer Data Query Tool")
st.divider()

# Initialize
@st.cache_resource
def init():
    init_database()
    seed_sample_data()
    seed_sample_documents()  # Initialize RAG
    return True

if not init():
    st.error("Failed to initialize")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📌 Navigation")
    page = st.radio("Select:", [
        "Customer Profile", 
        "Support Tickets",
        "AI Chatbot",
        "Document Search",
        "Upload Documents"
    ])

if page == "Customer Profile":
    st.header("Customer Profile")
    all_customers = search_customers("")
    if all_customers:
        name_email_options = [f"{c['name']} ({c['email']})" for c in all_customers]
        selected_option = st.selectbox("Select customer:", name_email_options)
        # Extract name from "Name (email)"
        selected = selected_option.split(" (")[0]
        profile = get_customer_profile(selected)
        if profile and "error" not in profile:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Customer ID", profile.get("id", "N/A"))
            with col2:
                st.metric("Email", profile.get("email", "N/A"))
            with col3:
                st.metric("Status", profile.get("account_status", "N/A"))
            with col4:
                st.metric("Account Type", profile.get("account_type", "N/A"))
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Contact")
                st.write(f"Phone: {profile.get('phone', 'N/A')}")
                st.write(f"Since: {profile.get('signup_date', 'N/A')}")
            with col2:
                st.subheader("Stats")
                st.write(f"Total Orders: {profile.get('total_orders', 0)}")
                st.write(f"Lifetime Value: ${profile.get('lifetime_value', 0):.2f}")
            if profile.get("orders"):
                st.divider()
                st.subheader("Orders")
                for order in profile["orders"]:
                    st.write(f"- Order #{order['id']}: ${order['amount']} ({order['status']}) - {order['order_date']}")
# Page: Tickets
elif page == "Support Tickets":
    st.header("Support Tickets")
    
    all_customers = search_customers("")
    if all_customers:
        name_email_options = [f"{c['name']} ({c['email']})" for c in all_customers]
        selected_option = st.selectbox("Select customer:", name_email_options, key="ticket_select")
        # Extract name from "Name (email)"
        selected = selected_option.split(" (")[0]
        tickets = get_customer_support_tickets(selected)
        
        if tickets and not tickets.get("error"):
            st.metric("Total Tickets", tickets.get("total_tickets", 0))
            
            if tickets.get("total_tickets", 0) > 0:
                st.divider()
                for ticket in tickets.get("tickets", []):
                    with st.expander(f"[{ticket['status'].upper()}] {ticket['title']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Priority:** {ticket['priority']}")
                        with col2:
                            st.write(f"**Category:** {ticket['category']}")
                        with col3:
                            st.write(f"**Created:** {ticket['created_date']}")
                        
                        st.write(f"{ticket.get('description', 'N/A')}")

# Page: AI Chatbot
elif page == "AI Chatbot":
    st.header("AI Customer Support Chatbot")
    st.markdown("Ask questions about our policies and get intelligent answers powered by Google Gemini")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.warning("⚠️ **API Key Required**")
        st.info("""
        To use the AI Chatbot, you need to:
        1. Get a **FREE** API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Add it to your `.env` file: `GOOGLE_API_KEY=your_key`
        3. Restart Streamlit
        
        Google's free tier includes:
        - 60 requests per minute
        - Unlimited requests per month (rate limited)
        - Perfect for development and testing!
        """)
    else:
        st.success("✅ API Key Found!")
        # Chat interface
        user_query = st.text_input("Ask a question about our policies:")
        
        if user_query:
            with st.spinner("🤖 Thinking..."):
                try:
                    result = generate_answer(user_query, n_results=5)
                    
                    # Display answer
                    st.success("✅ Answer Generated")
                    st.markdown("### Answer")
                    st.write(result["answer"])
                    
                    # Display sources
                    if result.get("sources"):
                        st.divider()
                        st.markdown("### 📚 Sources")
                        
                        for source in result["sources"]:
                            with st.expander(f"Source {source['id']}: {source['filename']} ({source['relevance']} relevant)"):
                                st.caption(f"Type: {source['type']}")
                    
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
                    st.info("Make sure your GOOGLE_API_KEY is valid and you have internet connection.")

# Page: Policies & FAQs (RAG)
elif page == "Document Search":
    st.header("Policies & FAQs")
    st.markdown("Search our knowledge base")
    
    query = st.text_input("Ask a question about policies, shipping, returns, etc.")
    
    if query:
        results = search_documents("policies_faqs", query, n_results=3)
        
        if results:
            st.success(f"Found {len(results)} relevant answer(s)")
            
            for i, result in enumerate(results, 1):
                similarity = result["similarity"]
                content = result["content"]
                metadata = result["metadata"]
                
                with st.expander(f"📄 Result {i} (Relevance: {similarity:.0%})", expanded=i==1):
                    st.write(content)
                    if metadata.get("type"):
                        st.caption(f"Type: {metadata['type']} | Category: {metadata.get('category', 'N/A')}")
        else:
            st.info("No results found. Try rephrasing your question.")

# Page: Upload Documents
elif page == "Upload Documents":
    st.header("Upload Policy Documents")
    st.markdown("Upload text or PDF files to add to the knowledge base")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["txt", "pdf", "md"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) ready to upload")
        
        if st.button("Process & Upload Documents"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            documents = []
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
                try:
                    # Read file content
                    content = file.read().decode("utf-8")
                    
                    documents.append({
                        "id": file.name.replace(".", "_"),
                        "content": content,
                        "metadata": {
                            "filename": file.name,
                            "file_type": file.type,
                            "source": "user_upload"
                        }
                    })
                except Exception as e:
                    st.error(f"Error reading {file.name}: {str(e)}")
            
            if documents:
                try:
                    n_chunks = add_documents("policies_faqs", documents)
                    
                    st.success(f"✅ Successfully uploaded {len(documents)} document(s) ({n_chunks} chunks)")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error uploading documents: {str(e)}")
    
    st.divider()
    st.subheader("📊 Knowledge Base Status")
    
    info = get_collection_info("policies_faqs")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Documents in KB", info.get("count", 0))
    with col2:
        st.metric("Status", "Ready" if info.get("count", 0) > 0 else "Empty")

st.divider()
st.markdown("**TCS Multi-Agent GenAI** - Structured Data Edition")
