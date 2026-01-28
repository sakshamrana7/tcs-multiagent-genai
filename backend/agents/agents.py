"""
Agents for handling different types of queries.
- PolicyAgent: Handles policy-related questions using RAG
- CustomerAgent: Handles customer data queries from SQL database
"""

import json
from typing import Dict, Any
from datetime import datetime
from backend.db.database import (
    get_customer_profile,
    get_customer_support_tickets,
    search_customers
)
from backend.rag.rag_pipeline import (
    query_policy_documents,
    get_policy_summary
)


class PolicyAgent:
    """Agent for answering policy-related questions using RAG."""

    def __init__(self):
        self.name = "PolicyAgent"
        self.description = "Answers questions about company policies"

    def process_query(self, question: str) -> Dict[str, Any]:
        """
        Process a policy question.
        
        Args:
            question: The user's question about policies
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Check if it's asking for a specific policy summary
        policy_keywords = {
            "refund": "refund_policy",
            "warranty": "warranty_policy",
            "shipping": "shipping_policy",
            "privacy": "privacy_policy",
            "terms": "terms_of_service"
        }

        for keyword, policy_name in policy_keywords.items():
            if keyword.lower() in question.lower():
                summary = get_policy_summary(policy_name)
                return {
                    "agent": self.name,
                    "type": "policy_summary",
                    "policy": policy_name.replace("_", " ").title(),
                    "content": summary,
                    "timestamp": datetime.now().isoformat()
                }

        # Otherwise, use RAG to answer the question
        result = query_policy_documents(question, top_k=3)

        return {
            "agent": self.name,
            "type": "policy_query",
            "question": result.get("question"),
            "answer": result.get("answer"),
            "sources": result.get("sources", []),
            "timestamp": datetime.now().isoformat()
        }


class CustomerAgent:
    """Agent for retrieving and summarizing customer data."""

    def __init__(self):
        self.name = "CustomerAgent"
        self.description = "Retrieves and summarizes customer profiles and support history"

    def process_query(self, question: str) -> Dict[str, Any]:
        """
        Process a customer data query.
        
        Args:
            question: The user's question about a customer
            
        Returns:
            Dictionary with customer information
        """
        # Extract customer name from question
        customer_name = self._extract_customer_name(question)

        if not customer_name:
            return {
                "agent": self.name,
                "type": "error",
                "message": "Could not identify customer name in question. Please specify the customer name.",
                "timestamp": datetime.now().isoformat()
            }

        # Determine what information is requested
        result = {}

        if any(word in question.lower() for word in ["profile", "customer info", "account", "details"]):
            profile = get_customer_profile(customer_name)
            result["profile"] = profile

        if any(word in question.lower() for word in ["ticket", "support", "issue", "complaint", "history"]):
            tickets = get_customer_support_tickets(customer_name)
            result["tickets"] = tickets

        # If no specific request, return both
        if not result:
            profile = get_customer_profile(customer_name)
            tickets = get_customer_support_tickets(customer_name)
            result["profile"] = profile
            result["tickets"] = tickets

        return {
            "agent": self.name,
            "type": "customer_query",
            "question": question,
            "customer_name": customer_name,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_customer_name(self, question: str) -> str:
        """
        Extract customer name from question.
        Looks for patterns like "customer X's profile" or "X's support tickets"
        """
        # Simple extraction - split by common keywords
        keywords = ["customer", "for", "profile", "tickets", "about"]

        words = question.split()
        for i, word in enumerate(words):
            if word.lower() in keywords and i + 1 < len(words):
                # Get next word as potential customer name
                potential_name = words[i + 1].strip("'s,.")
                if potential_name and not potential_name.lower() in keywords:
                    return potential_name

        # Try to extract quoted name
        import re
        match = re.search(r"['\"]([^'\"]+)['\"]", question)
        if match:
            return match.group(1)

        # Try to extract capitalized words (likely names)
        names = [word.strip("'s,.") for word in words if word[0].isupper() and word.lower() not in keywords]
        if names:
            return " ".join(names[:2])  # Take first two capitalized words

        return None


class MultiAgentOrchestrator:
    """Orchestrates multiple agents based on query type."""

    def __init__(self):
        self.policy_agent = PolicyAgent()
        self.customer_agent = CustomerAgent()

    def route_query(self, question: str) -> Dict[str, Any]:
        """
        Route the question to the appropriate agent.
        
        Args:
            question: The user's question
            
        Returns:
            Response from the appropriate agent
        """
        # Determine query type
        policy_keywords = ["policy", "refund", "warranty", "shipping", "privacy", "terms", "guarantee", "coverage"]
        customer_keywords = ["customer", "profile", "support ticket", "issue", "complaint", "order", "account"]

        question_lower = question.lower()
        is_policy_query = any(keyword in question_lower for keyword in policy_keywords)
        is_customer_query = any(keyword in question_lower for keyword in customer_keywords)

        # Route to appropriate agent
        if is_policy_query and not is_customer_query:
            return self.policy_agent.process_query(question)
        elif is_customer_query:
            return self.customer_agent.process_query(question)
        else:
            # Default: try policy agent first
            return self.policy_agent.process_query(question)

    def process(self, question: str) -> str:
        """
        Process a question and return a formatted response.
        
        Args:
            question: The user's question
            
        Returns:
            Formatted response string
        """
        result = self.route_query(question)

        if result.get("agent") == "PolicyAgent":
            if result.get("type") == "policy_summary":
                return f"**{result['policy']}**\n\n{result['content']}"
            else:
                return result.get("answer", "No answer found")

        elif result.get("agent") == "CustomerAgent":
            if result.get("type") == "error":
                return result.get("message", "Error processing query")
            else:
                # Format customer data response
                response = f"**Customer: {result.get('customer_name')}**\n\n"

                if "profile" in result.get("data", {}):
                    profile = result["data"]["profile"]
                    if "error" not in profile:
                        response += f"**Profile:**\n"
                        response += f"- Email: {profile.get('email')}\n"
                        response += f"- Phone: {profile.get('phone')}\n"
                        response += f"- Account Status: {profile.get('account_status')}\n"
                        response += f"- Account Type: {profile.get('account_type')}\n"
                        response += f"- Total Orders: {profile.get('total_orders')}\n"
                        response += f"- Lifetime Value: ${profile.get('lifetime_value')}\n\n"

                if "tickets" in result.get("data", {}):
                    tickets = result["data"]["tickets"]
                    if "tickets" in tickets and tickets["tickets"]:
                        response += f"**Support Tickets ({tickets.get('total_tickets')}):**\n"
                        for ticket in tickets["tickets"][:5]:  # Show last 5 tickets
                            response += f"- [{ticket['status'].upper()}] {ticket['title']} (Priority: {ticket['priority']})\n"

                return response

        return "Unable to process query"


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()
