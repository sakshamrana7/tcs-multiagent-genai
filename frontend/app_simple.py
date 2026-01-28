"""
Streamlit Web UI for TCS Multi-Agent GenAI Tool
Simple structured data interface
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.database import (
    init_database,
    seed_sample_data,
    get_customer_profile,
    get_customer_support_tickets,
    search_customers,
)

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
    return True

if not init():
    st.error("Failed to initialize")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📌 Navigation")
    page = st.radio("Select:", ["🔍 Search", "👤 Profile", "🎫 Tickets"])

# Page: Search
if page == "🔍 Search":
    st.header("Search Customers")
    query = st.text_input("Enter name or email:")
    
    if query:
        results = search_customers(query)
        if results:
            st.success(f"Found {len(results)} customer(s)")
            for c in results:
                st.write(f"**{c['name']}** - {c['email']} ({c['account_status']})")
        else:
            st.info("No results")

# Page: Profile
elif page == "👤 Profile":
    st.header("Customer Profile")
    
    all_customers = search_customers("")
    if all_customers:
        names = [c["name"] for c in all_customers]
        selected = st.selectbox("Select customer:", names)
        
        profile = get_customer_profile(selected)
        
        if profile and "error" not in profile:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Email", profile.get("email", "N/A"))
            with col2:
                st.metric("Status", profile.get("account_status", "N/A"))
            with col3:
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
elif page == "🎫 Tickets":
    st.header("Support Tickets")
    
    all_customers = search_customers("")
    if all_customers:
        names = [c["name"] for c in all_customers]
        selected = st.selectbox("Select customer:", names, key="ticket_select")
        
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

st.divider()
st.markdown("**TCS Multi-Agent GenAI** - Structured Data Edition")
