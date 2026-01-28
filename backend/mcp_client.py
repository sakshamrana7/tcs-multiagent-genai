"""
MCP Client for testing the Multi-Agent GenAI Server
Demonstrates calling various tools on the MCP server
"""

import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession


async def test_health():
    """Test health endpoint."""
    print("\n" + "="*50)
    print("Testing: Health Check")
    print("="*50)

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("health", {})
            print(result.content[0].text)


async def test_policy_query():
    """Test policy query tool."""
    print("\n" + "="*50)
    print("Testing: Policy Query")
    print("="*50)

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            question = "What is the current refund policy?"
            print(f"\nQuestion: {question}")

            result = await session.call_tool(
                "query_policy",
                {"question": question}
            )
            response = json.loads(result.content[0].text)
            print(f"\nAnswer: {response.get('answer', 'No answer')[:200]}...")
            print(f"Sources: {response.get('sources', [])}")


async def test_customer_query():
    """Test customer query tool."""
    print("\n" + "="*50)
    print("Testing: Customer Query")
    print("="*50)

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            question = "Give me a quick overview of customer Ema Johnson's profile and past support ticket details."
            print(f"\nQuestion: {question}")

            result = await session.call_tool(
                "query_customer",
                {"question": question}
            )
            response = json.loads(result.content[0].text)

            if "data" in response:
                if "profile" in response["data"]:
                    profile = response["data"]["profile"]
                    print(f"\n👤 Profile:")
                    print(f"  - Email: {profile.get('email')}")
                    print(f"  - Status: {profile.get('account_status')}")
                    print(f"  - Type: {profile.get('account_type')}")
                    print(f"  - Orders: {profile.get('total_orders')}")
                    print(f"  - Lifetime Value: ${profile.get('lifetime_value')}")

                if "tickets" in response["data"]:
                    tickets = response["data"]["tickets"]
                    print(f"\n🎫 Support Tickets ({tickets.get('total_tickets')}):")
                    for ticket in tickets.get('tickets', [])[:3]:
                        print(f"  - [{ticket['status'].upper()}] {ticket['title']}")


async def test_smart_query():
    """Test smart query tool."""
    print("\n" + "="*50)
    print("Testing: Smart Query")
    print("="*50)

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test policy question
            question1 = "What is the warranty coverage?"
            print(f"\nQuery 1: {question1}")

            result1 = await session.call_tool(
                "smart_query",
                {"question": question1}
            )
            response1 = json.loads(result1.content[0].text)
            print(f"Agent Used: {response1.get('agent_used')}")
            print(f"Response: {response1.get('response')[:150]}...")

            # Test customer question
            question2 = "Tell me about Sarah Chen's orders"
            print(f"\nQuery 2: {question2}")

            result2 = await session.call_tool(
                "smart_query",
                {"question": question2}
            )
            response2 = json.loads(result2.content[0].text)
            print(f"Agent Used: {response2.get('agent_used')}")
            print(f"Response: {response2.get('response')[:150]}...")


async def test_get_policy():
    """Test get_policy_document tool."""
    print("\n" + "="*50)
    print("Testing: Get Policy Document")
    print("="*50)

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            policy = "refund_policy"
            print(f"\nRetrieving: {policy}")

            result = await session.call_tool(
                "get_policy_document",
                {"policy_name": policy}
            )
            response = json.loads(result.content[0].text)
            print(f"\nContent: {response.get('content', '')[:300]}...")


async def test_search_customers():
    """Test search_customer_database tool."""
    print("\n" + "="*50)
    print("Testing: Search Customers")
    print("="*50)

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            query = "Ema"
            print(f"\nSearching for: {query}")

            result = await session.call_tool(
                "search_customer_database",
                {"query": query}
            )
            response = json.loads(result.content[0].text)
            print(f"Found {response.get('results_count')} results")

            for customer in response.get('results', []):
                print(f"  - {customer['name']} ({customer['email']})")


async def main():
    """Run all tests."""
    print("\n" + "🚀 "*25)
    print("MCP SERVER TEST SUITE")
    print("🚀 "*25)

    try:
        await test_health()
        await test_policy_query()
        await test_customer_query()
        await test_smart_query()
        await test_get_policy()
        await test_search_customers()

        print("\n" + "="*50)
        print("✅ All tests completed!")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

