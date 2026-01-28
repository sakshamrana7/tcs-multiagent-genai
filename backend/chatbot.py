"""
Chatbot module combining RAG + LLM for intelligent responses
Multi-agent system that handles both policy questions and customer queries
"""

from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.rag.rag_pipeline import search_documents
from backend.db.database import search_customers, get_customer_profile, get_customer_support_tickets
import os


def create_chatbot(model: str = "gemini-2.5-flash", temperature: float = 0.7):
    """
    Create a Google Gemini chatbot.
    
    Args:
        model: Model name (gemini-2.5-flash, gemini-2.5-flash-lite, etc.)
        temperature: Controls randomness (0-1, lower = more deterministic)
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not set. Please set your API key in .env file or environment."
        )
    
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key
    )


def generate_answer(
    query: str,
    llm=None,
    n_results: int = 5,
    collection_name: str = "policies_faqs"
) -> Dict[str, Any]:
    """
    Generate an answer using multi-agent RAG + customer database + LLM.
    Routes queries to both policy documents and customer database as needed.
    
    Args:
        query: User's question
        llm: ChatGoogleGenerativeAI instance (created if not provided)
        n_results: Number of context chunks to retrieve
        collection_name: ChromaDB collection to search
    
    Returns:
        Dict with answer, sources, and metadata
    """
    if llm is None:
        llm = create_chatbot()
    
    import re
    
    # Step 1: Detect query type - check if customer names are mentioned
    query_lower = query.lower()
    
    # Get all customer names from database for matching
    customer_names = []
    try:
        all_customers = search_customers("")  # Get all customers
        customer_names = [cust.get("name", "").lower() for cust in all_customers]
    except:
        pass
    
    # Check if any customer names appear in the query
    is_customer_query = any(name in query_lower for name in customer_names) or any(
        keyword in query_lower for keyword in [
            "customer", "profile", "order", "ticket", "support", "history", "past", "recent",
            "account", "contact", "invoice", "purchase", "transaction"
        ]
    )
    
    # Keywords for policy queries
    policy_keywords = [
        "policy", "faq", "return", "refund", "shipping", "payment", "exchange",
        "warranty", "guarantee", "rules", "guidelines", "terms", "condition",
        "process", "procedure", "how", "what is", "explain"
    ]
    
    is_policy_query = any(keyword in query_lower for keyword in policy_keywords)
    
    # If no keywords detected, assume it could be either - try customer search first
    if not is_customer_query and not is_policy_query:
        is_customer_query = True
    
    # Extract customer names from database for smarter matching
    all_customer_names = []  # Will store (full_name, lowercase_name) tuples
    try:
        all_db_customers = search_customers("")  # Get all customers
        all_customer_names = [(cust.get("name", ""), cust.get("name", "").lower()) for cust in all_db_customers]
    except:
        pass
    
    # Check if any actual customer names are mentioned in the query
    mentioned_customer_data = []
    for full_name, lower_name in all_customer_names:
        if lower_name and lower_name in query_lower:
            mentioned_customer_data.append((full_name, lower_name))
    
    # Step 2: Retrieve context from appropriate sources
    all_context = []
    all_sources = []
    source_counter = 1
    
    # Retrieve customer database context if relevant
    customer_context = ""
    if is_customer_query:
        try:
            customer_results = None
            
            # Priority 1: If actual customer names are mentioned, search for them
            if mentioned_customer_data:
                for full_name, lower_name in mentioned_customer_data:
                    customer_results = search_customers(full_name)
                    if customer_results:
                        break
            else:
                # Priority 2: Try searching with the full query
                customer_results = search_customers(query)
            
            if customer_results:
                customer_context = "=== CUSTOMER DATABASE RESULTS ===\n"
                for customer in customer_results:
                    customer_id = customer.get("id", "")
                    customer_name = customer.get("name", "")
                    
                    # Get detailed profile
                    try:
                        profile = get_customer_profile(customer_id)
                        profile_text = f"\nCustomer: {customer_name}\nEmail: {profile.get('email', 'N/A')}\nPhone: {profile.get('phone', 'N/A')}\nAddress: {profile.get('address', 'N/A')}\nAccount Status: {profile.get('account_status', 'N/A')}"
                    except:
                        profile_text = f"\nCustomer: {customer_name}"
                    
                    customer_context += profile_text
                    
                    # Get support tickets
                    try:
                        tickets = get_customer_support_tickets(customer_id)
                        if tickets:
                            customer_context += f"\n\nSupport Tickets ({len(tickets)}):\n"
                            for ticket in tickets[:3]:  # Limit to 3 most recent
                                customer_context += f"  - {ticket.get('subject', 'N/A')}: {ticket.get('status', 'N/A')}\n"
                    except:
                        pass
                    
                    customer_context += "\n"
                
                all_context.append(f"[Source {source_counter}]\n{customer_context.strip()}")
                all_sources.append({
                    "id": source_counter,
                    "filename": "customer_database",
                    "relevance": "100%",
                    "type": "customer_data"
                })
                source_counter += 1
        except Exception as e:
            # If database query fails, continue with policy search
            pass
    
    # Retrieve policy/FAQ context if relevant
    if is_policy_query:
        search_results = search_documents(collection_name, query, n_results=n_results)
        
        if search_results:
            for result in search_results:
                content = result.get("content", "")
                metadata = result.get("metadata", {})
                similarity = result.get("similarity", 0)
                
                all_context.append(f"[Source {source_counter}]\n{content}")
                
                filename = metadata.get("filename", "document")
                if filename.endswith((".txt", ".pdf", ".md")):
                    filename = filename.rsplit(".", 1)[0]
                
                all_sources.append({
                    "id": source_counter,
                    "filename": filename,
                    "relevance": f"{similarity:.0%}",
                    "type": metadata.get("type", "document")
                })
                source_counter += 1
    
    # If no context found from any source
    if not all_context:
        return {
            "answer": "I couldn't find relevant information. Please provide more specific details or check your uploaded documents.",
            "sources": [],
            "has_context": False,
            "query": query
        }
    
    context = "\n\n".join(all_context)
    
    # Step 3: Create system and user prompts for multi-agent response
    system_prompt = """You are a knowledgeable multi-agent customer support assistant for TCS.
    You have access to:
    1. Customer database (profiles, orders, support tickets)
    2. Company policies, FAQs, and guidelines
    
    Your role is to answer questions using the provided context from both sources.
    Always be helpful, accurate, and professional.
    If information comes from customer data, acknowledge it clearly.
    If information comes from policies, cite the policy source when relevant."""
    
    user_prompt = f"""Available Information:

{context}

---

Customer Question: {query}

Please provide a comprehensive answer using any relevant information from the sources above."""
    
    # Step 4: Generate response using LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    answer_text = response.content
    # Remove inline source citations
    answer_text = re.sub(r'\s*[\[\(]Source\s+[^\]\)]*[\]\)]', '', answer_text)
    answer_text = answer_text.strip()
    
    return {
        "answer": answer_text,
        "sources": all_sources,
        "has_context": True,
        "query": query
    }


if __name__ == "__main__":
    # Test the chatbot
    import os
    
    # Make sure API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Please set GOOGLE_API_KEY environment variable")
        print("Get your free key from: https://aistudio.google.com/app/apikey")
    else:
        print("Testing chatbot...")
        result = generate_answer("What is your return policy?")
        print(f"\nQuestion: {result['query']}")
        print(f"Answer: {result['answer']}")
        print(f"\nSources: {result['sources']}")
