"""
Streamlit Web UI for TCS Multi-Agent GenAI Tool
Provides interactive interface for customer data retrieval
"""

import streamlit as st
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.database import (
    init_database,
    seed_sample_data,
    get_customer_profile,
    get_customer_support_tickets,
    search_customers,
)

# Page configuration
st.set_page_config(
    page_title="TCS Multi-Agent GenAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .agent-response {
        background-color: #e8f4f8;
        padding: 15px;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin-top: 10px;
    }
    .error-response {
        background-color: #ffe8e8;
        padding: 15px;
        border-left: 4px solid #ff4444;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize database on first load."""
    try:
        init_database()
        seed_sample_data()
        return True
    except Exception as e:
        st.error(f"Initialization error: {e}")
        return False


def format_response(result):
    """Format agent response for display."""
    if result.get("agent") == "PolicyAgent":
        if result.get("type") == "policy_summary":
            return f"""
            **Policy:** {result['policy']}
            
            {result['content']}
            """
        else:
            return f"""
            **Question:** {result.get('question')}
            
            **Answer:**
            {result.get('answer')}
            
            **Sources:** {', '.join(result.get('sources', []))}
            """

    elif result.get("agent") == "CustomerAgent":
        if result.get("type") == "error":
            return result.get("message", "Error processing query")
        else:
            response = f"**Customer:** {result.get('customer_name')}\n\n"

            if "profile" in result.get("data", {}):
                profile = result["data"]["profile"]
                if "error" not in profile:
                    response += f"""**Profile Information:**
- **Email:** {profile.get('email')}
- **Phone:** {profile.get('phone')}
- **Account Status:** {profile.get('account_status')}
- **Account Type:** {profile.get('account_type')}
- **Total Orders:** {profile.get('total_orders')}
- **Lifetime Value:** ${profile.get('lifetime_value'):.2f}

"""

            if "tickets" in result.get("data", {}):
                tickets = result["data"]["tickets"]
                if "tickets" in tickets and tickets["tickets"]:
                    response += f"**Support Tickets ({tickets.get('total_tickets')}):**\n"
                    for ticket in tickets["tickets"]:
                        response += f"""
- **[{ticket['status'].upper()}]** {ticket['title']}
  - Priority: {ticket['priority']}
  - Category: {ticket['category']}
  - Created: {ticket['created_date']}
"""

            return response

    return "Unable to format response"


def main():
    """Main application function."""
    # Initialize system
    if not initialize_system():
        st.error("Failed to initialize system. Please check your setup.")
        return

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)

        st.subheader("Query Type")
        query_mode = st.radio(
            "Select query type:",
            ["🤖 Smart Query", "📋 Policy Questions", "👤 Customer Data"],
            index=0
        )

        st.divider()

        st.subheader("Sample Queries")
        st.markdown("""
        **Policy Questions:**
        - What is the current refund policy?
        - Tell me about warranty coverage
        - What's your shipping timeline?
        - How do you handle privacy?
        
        **Customer Queries:**
        - Give me a quick overview of customer Ema Johnson's profile
        - What are John Smith's past support tickets?
        - Show me Sarah Chen's account details
        """)

        st.divider()

        st.subheader("Sample Data")
        if st.button("📊 View Sample Customers"):
            st.info("Sample customers in database:")
            st.code("""
- Ema Johnson (Premium)
- John Smith (Standard)
- Sarah Chen (Premium)
- Michael Davis (Standard)
- Lisa Anderson (Standard)
            """)

        if st.button("📄 View Available Policies"):
            st.info("Available policy documents:")
            st.code("""
- Refund Policy
- Warranty Policy
- Shipping Policy
- Privacy Policy
- Terms of Service
            """)

    # Main content
    st.markdown('<div class="main-header">🤖 TCS Multi-Agent GenAI Assistant</div>', unsafe_allow_html=True)

    st.markdown("""
    Welcome to the TCS Multi-Agent GenAI Tool! This assistant can help you with:
    
    ✅ **Policy Questions** - Get detailed answers about company policies using RAG
    
    ✅ **Customer Information** - Retrieve customer profiles and support tickets from the database
    
    ✅ **Smart Routing** - Automatically route your question to the right agent
    """)

    st.divider()

    # Query input
    st.subheader("Ask a Question")

    if query_mode == "🤖 Smart Query":
        user_input = st.text_input(
            "Enter your question (can be about customers):",
            placeholder="E.g., 'Tell me about customer Ema Johnson' or 'What are John Smith's tickets?'"
        )

        if st.button("🚀 Submit Query", type="primary"):
            if user_input:
                with st.spinner("Processing your question..."):
                    # For now, redirect to customer data search
                    st.info("Smart Query mode currently supports customer data queries.")
                    st.markdown('<div class="agent-response">', unsafe_allow_html=True)
                    st.markdown("Please use the 'Customer Data' tab for structured data queries.")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter a question")

    elif query_mode == "📋 Policy Questions":
        st.info("Policy RAG system has been removed. Currently supporting structured customer data only.")

    elif query_mode == "👤 Customer Data":
        user_input = st.text_input(
            "Enter customer name or search query:",
            placeholder="E.g., 'Ema Johnson' or 'customer Ema Johnson's profile'"
        )

        col1, col2 = st.columns(2)

        with col1:
            search_mode = st.radio(
                "What would you like to see?",
                ["Profile & Orders", "Support Tickets", "Both"]
            )

        if st.button("🔍 Search Customer", type="primary"):
            if user_input:
                with st.spinner("Searching customer database..."):
                    try:
                        if search_mode == "Profile & Orders":
                            data = get_customer_profile(user_input)
                            st.markdown('<div class="agent-response">', unsafe_allow_html=True)
                            st.markdown(f"## {user_input}")

                            if "error" not in data:
                                st.markdown("""
                                **Account Information:**
                                """)
                                cols = st.columns(2)
                                with cols[0]:
                                    st.metric("Account Status", data.get('account_status', 'N/A').upper())
                                    st.metric("Account Type", data.get('account_type', 'N/A').title())

                                with cols[1]:
                                    st.metric("Total Orders", data.get('total_orders', 0))
                                    st.metric("Lifetime Value", f"${data.get('lifetime_value', 0):.2f}")

                                st.markdown(f"""
                                - **Email:** {data.get('email')}
                                - **Phone:** {data.get('phone')}
                                - **Signup Date:** {data.get('signup_date')}
                                """)

                                if data.get('orders'):
                                    st.markdown("**Recent Orders:**")
                                    for order in data.get('orders', [])[:3]:
                                        st.write(f"- Order #{order['id']}: ${order['amount']} ({order['status']}) - {order['order_date']}")
                            else:
                                st.error(data.get('error'))

                            st.markdown('</div>', unsafe_allow_html=True)

                        elif search_mode == "Support Tickets":
                            data = get_customer_support_tickets(user_input)
                            st.markdown('<div class="agent-response">', unsafe_allow_html=True)
                            st.markdown(f"## {user_input} - Support Tickets")

                            if "error" not in data:
                                st.metric("Total Tickets", data.get('total_tickets', 0))

                                for ticket in data.get('tickets', []):
                                    with st.expander(f"[{ticket['status'].upper()}] {ticket['title']}"):
                                        st.write(f"**Priority:** {ticket['priority']}")
                                        st.write(f"**Category:** {ticket['category']}")
                                        st.write(f"**Created:** {ticket['created_date']}")
                                        st.write(f"**Status:** {ticket['status']}")
                                        st.write(f"\n{ticket['description']}")
                            else:
                                st.error(data.get('error'))

                            st.markdown('</div>', unsafe_allow_html=True)

                        else:  # Both
                            profile = get_customer_profile(user_input)
                            tickets = get_customer_support_tickets(user_input)

                            st.markdown('<div class="agent-response">', unsafe_allow_html=True)
                            st.markdown(f"## {user_input}")

                            if "error" not in profile:
                                st.markdown("### Profile Information")
                                cols = st.columns(2)
                                with cols[0]:
                                    st.metric("Account Status", profile.get('account_status', 'N/A').upper())
                                    st.metric("Total Orders", profile.get('total_orders', 0))

                                with cols[1]:
                                    st.metric("Account Type", profile.get('account_type', 'N/A').title())
                                    st.metric("Lifetime Value", f"${profile.get('lifetime_value', 0):.2f}")

                            if "error" not in tickets and tickets.get('total_tickets', 0) > 0:
                                st.markdown("### Recent Support Tickets")
                                for ticket in tickets.get('tickets', [])[:5]:
                                    st.write(f"- [{ticket['status'].upper()}] {ticket['title']} ({ticket['priority']} priority)")

                            st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.markdown('<div class="error-response">', unsafe_allow_html=True)
                        st.error(f"Error retrieving customer data: {str(e)}")
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter a customer name")

    # Chat history
    st.divider()
    st.subheader("💬 About This Tool")

    with st.expander("System Architecture"):
        st.markdown("""
        **Components:**
        
        1. **Multi-Agent System** - Intelligent routing based on query type
        2. **RAG (Retrieval Augmented Generation)** - Policy document retrieval
        3. **SQL Database** - Customer data and support tickets
        4. **MCP Server** - Backend service layer
        5. **Streamlit UI** - Interactive web interface
        
        **Technology Stack:**
        - LangChain for agent orchestration
        - ChromaDB for vector storage
        - SQLite for structured data
        - Streamlit for web interface
        """)

    with st.expander("Features"):
        st.markdown("""
        ✅ **Intelligent Query Routing** - Automatically determines if a question is about policies or customers
        
        ✅ **Policy RAG** - Get detailed answers from company policy documents
        
        ✅ **Customer Database** - Access customer profiles, orders, and support history
        
        ✅ **Smart Search** - Find customers by name, email, or phone
        
        ✅ **Structured Data** - Support ticket tracking and order management
        """)


if __name__ == "__main__":
    main()
