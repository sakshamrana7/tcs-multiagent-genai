"""
MCP Server for Multi-Agent GenAI Tool
Provides tools for policy RAG and customer data queries
"""

from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.agents.agents import orchestrator, PolicyAgent, CustomerAgent
from backend.db.database import (
    init_database,
    seed_sample_data,
    get_customer_profile,
    get_customer_support_tickets,
    search_customers,
    query_database
)
from backend.rag.rag_pipeline import (
    query_policy_documents,
    get_policy_summary,
    create_sample_policy_documents
)

# Initialize MCP server
mcp = FastMCP("TCS Multi-Agent GenAI Server")

# Initialize database and RAG on startup
try:
    init_database()
    seed_sample_data()
    print("✓ Database initialized", file=__import__("sys").stderr)
except Exception as e:
    print(f"✗ Database initialization error: {e}", file=__import__("sys").stderr)

try:
    create_sample_policy_documents()
    print("✓ Policy documents created", file=__import__("sys").stderr)
except Exception as e:
    print(f"✗ RAG initialization error: {e}", file=__import__("sys").stderr)


@mcp.tool()
def health() -> str:
    """Health check endpoint."""
    return json.dumps({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TCS Multi-Agent GenAI Server",
        "version": "1.0.0"
    })


@mcp.tool()
def query_policy(question: str) -> str:
    """
    Query policy documents using RAG.
    
    Args:
        question: Question about company policies
        
    Returns:
        JSON response with answer and sources
    """
    try:
        result = orchestrator.policy_agent.process_query(question)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "type": "policy_query",
            "question": question,
            "timestamp": datetime.now().isoformat()
        })


@mcp.tool()
def query_customer(question: str) -> str:
    """
    Query customer data from SQL database.
    Retrieves customer profiles and support tickets.
    
    Args:
        question: Question about a customer (e.g., "What is Ema Johnson's profile?")
        
    Returns:
        JSON response with customer information
    """
    try:
        result = orchestrator.customer_agent.process_query(question)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "type": "customer_query",
            "question": question,
            "timestamp": datetime.now().isoformat()
        })


@mcp.tool()
def get_customer_info(customer_name: str) -> str:
    """
    Get detailed customer profile information.
    
    Args:
        customer_name: Name of the customer
        
    Returns:
        JSON with customer profile and orders
    """
    try:
        profile = get_customer_profile(customer_name)
        return json.dumps({
            "customer": customer_name,
            "profile": profile,
            "timestamp": datetime.now().isoformat()
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "customer": customer_name
        })


@mcp.tool()
def get_customer_tickets(customer_name: str) -> str:
    """
    Get support tickets for a customer.
    
    Args:
        customer_name: Name of the customer
        
    Returns:
        JSON with support ticket history
    """
    try:
        tickets = get_customer_support_tickets(customer_name)
        return json.dumps({
            "customer": customer_name,
            "tickets": tickets,
            "timestamp": datetime.now().isoformat()
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "customer": customer_name
        })


@mcp.tool()
def search_customer_database(query: str) -> str:
    """
    Search customers by name, email, or phone.
    
    Args:
        query: Search term (name, email, or phone)
        
    Returns:
        JSON with matching customers
    """
    try:
        results = search_customers(query)
        return json.dumps({
            "query": query,
            "results_count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "query": query
        })


@mcp.tool()
def get_policy_document(policy_name: str) -> str:
    """
    Retrieve a full policy document.
    
    Available policies:
    - refund_policy
    - warranty_policy
    - shipping_policy
    - privacy_policy
    - terms_of_service
    
    Args:
        policy_name: Name of the policy (without .txt)
        
    Returns:
        Policy document content
    """
    try:
        content = get_policy_summary(policy_name)
        return json.dumps({
            "policy": policy_name,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "policy": policy_name
        })


@mcp.tool()
def smart_query(question: str) -> str:
    """
    Smart query router - automatically determines if question is about
    policies or customer data and routes accordingly.
    
    Args:
        question: Any question about policies or customers
        
    Returns:
        Formatted response from appropriate agent
    """
    try:
        result = orchestrator.route_query(question)
        response = orchestrator.process(question)
        
        return json.dumps({
            "question": question,
            "agent_used": result.get("agent"),
            "response": response,
            "metadata": {
                "type": result.get("type"),
                "timestamp": datetime.now().isoformat()
            }
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "question": question,
            "timestamp": datetime.now().isoformat()
        })


@mcp.tool()
def execute_sql_query(sql_query: str) -> str:
    """
    Execute a SELECT query on the customer database.
    Only SELECT queries are allowed for security.
    
    Args:
        sql_query: SELECT query to execute
        
    Returns:
        Query results as JSON
    """
    try:
        if not sql_query.strip().upper().startswith("SELECT"):
            return json.dumps({
                "error": "Only SELECT queries are allowed"
            })

        results = query_database(sql_query)
        return json.dumps({
            "query": sql_query,
            "results_count": len(results) if isinstance(results, list) else 0,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "query": sql_query
        })


if __name__ == "__main__":
    mcp.run()
