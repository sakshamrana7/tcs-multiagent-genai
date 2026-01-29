# TCS Multi-Agent GenAI Tool

## 🚦 Quick Start (TL;DR)

```bash
cd /Users/sakshamrana/Documents/GitHub/tcs-multiagent-genai
pip install -r backend/requirements.txt

# Start the app (default port 8501)
streamlit run frontend/app_simple.py

# Open http://localhost:8501 in your browser
```

For troubleshooting or advanced usage, see below.

A sophisticated multi-agent GenAI system that combines Retrieval Augmented Generation (RAG) for policy documents with SQL database queries for customer information. Built with LangChain, LangGraph, MCP Server, and Streamlit.

## 🎯 Features

### 1. **Policy RAG System**
- Upload and index company policy PDFs or documents
- Intelligent retrieval of relevant policy sections
- Context-aware answers to policy questions
- Support for multiple policy documents (Refund, Warranty, Shipping, Privacy, Terms)

### 2. **Customer Data System**
- Structured customer profiles and account information
- Support ticket history and tracking
- Order management and history
- Search customers by name, email, or phone

### 3. **Multi-Agent Orchestration**
- **PolicyAgent**: Handles policy-related queries using RAG
- **CustomerAgent**: Retrieves and summarizes customer data
- **Smart Router**: Automatically routes queries to appropriate agent

### 4. **Flexible Backend**
- MCP (Model Context Protocol) Server for agent communication
- RESTful API architecture
- Async request handling

### 5. **User-Friendly Interface**
- Interactive Streamlit web application
- Smart query interface with mode selection
- Quick access buttons for common policies
- Customer search and profile viewing

## 🏗️ Architecture

```
tcs-multiagent-genai/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agents.py          # PolicyAgent, CustomerAgent, Orchestrator
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite setup, customer data functions
│   │   └── customers.db        # SQLite database (auto-created)
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── rag_pipeline.py     # RAG setup, document loading, querying
│   │   ├── docs/               # Policy documents
│   │   └── chroma_db/          # Vector store (auto-created)
│   ├── mcp_server.py           # MCP server with tools
│   ├── mcp_client.py           # MCP client for testing
│   └── requirements.txt        # Python dependencies
├── frontend/
│   └── app.py                  # Streamlit web interface
└── README.md
```

## 📋 Technology Stack

**Core Libraries:**
- **LangChain** (0.1.0+) - Agent orchestration and chains
- **LangGraph** (0.1.0+) - Graph-based agent workflows
- **MCP** (0.5.0+) - Model Context Protocol server

**Models & Embeddings:**
- LLM: OpenAI, Anthropic, or local alternatives
- Embeddings: OllamaEmbeddings or FakeEmbeddings for testing

**Databases:**
- **SQLite** - Customer data, orders, support tickets
- **ChromaDB** (4.4.0+) - Vector store for policy embeddings

**Web & UI:**
- **Streamlit** (1.28.0+) - Interactive web interface
- **FastAPI** (0.100.0+) - API framework
- **Uvicorn** (0.24.0+) - ASGI server

**Data Processing:**
- Pandas, NumPy - Data manipulation
- PyPDF, PDFPlumber - PDF processing

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
cd /Users/sakshamrana/Documents/GitHub/tcs-multiagent-genai

# Install all requirements
pip install -r backend/requirements.txt
```

### 2. **Initialize System**

The system initializes automatically on first run. To manually initialize:

```bash
# Initialize database and RAG
python -c "from backend.db.database import init_database, seed_sample_data; init_database(); seed_sample_data()"
python -c "from backend.rag.rag_pipeline import create_sample_policy_documents; create_sample_policy_documents()"
```

### 3. **Run the Web Interface**

```bash
streamlit run frontend/app.py
```

The app will open at `http://localhost:8501`

### 4. **Test MCP Server**

```bash
# Start server in one terminal
python backend/mcp_server.py

# Run tests in another terminal
python backend/mcp_client.py
```

## 📖 Usage Examples

### Via Streamlit Web Interface

1. **Ask a Policy Question:**
   - Select "📋 Policy Questions" mode
   - Enter: "What is the current refund policy?"
   - Click "View Refund Policy" button or submit the question

2. **Search Customer Data:**
   - Select "👤 Customer Data" mode
   - Enter: "Ema Johnson"
   - Choose view type (Profile, Tickets, or Both)
   - Click "Search Customer"

3. **Smart Query:**
   - Select "🤖 Smart Query" mode
   - Ask any question (auto-routed to appropriate agent)
   - Examples:
     - "What is our warranty policy?" → PolicyAgent
     - "Tell me about Sarah Chen's profile" → CustomerAgent

### Via MCP Server

```python
# Example: Query policy
result = await session.call_tool("query_policy", {
    "question": "What is the refund policy?"
})

# Example: Get customer info
result = await session.call_tool("query_customer", {
    "question": "Give me overview of customer Ema Johnson's profile"
})

# Example: Smart routing
result = await session.call_tool("smart_query", {
    "question": "Tell me about warranty"
})
```

## 📊 Sample Data

### Customers
- **Ema Johnson** (Premium) - 12 orders, $4,500 lifetime value
- **John Smith** (Standard) - 5 orders, $1,200 lifetime value
- **Sarah Chen** (Premium) - 25 orders, $8,900 lifetime value
- **Michael Davis** (Standard) - 3 orders, $650 lifetime value
- **Lisa Anderson** (Standard, Inactive) - 8 orders, $1,800 lifetime value

### Policy Documents
- **Refund Policy** - 30/60/90 day windows, process, special cases
- **Warranty Policy** - 1-2 year coverage, defect handling
- **Shipping Policy** - Delivery timeframes, costs, tracking
- **Privacy Policy** - Data collection, usage, protection
- **Terms of Service** - Acceptable use, liability, dispute resolution

### Support Tickets
Each customer has related support tickets with:
- Status (open, closed, pending)
- Priority levels
- Category (refund, technical, shipping, quality, account)
- Descriptions and timestamps

## 🔧 Configuration

### Environment Variables (Optional)

Create `.env` file in the root directory:

```bash
# LLM Configuration
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DB_PATH=./backend/db/customers.db

# RAG
DOCS_PATH=./backend/rag/docs
CHROMA_DB_PATH=./backend/rag/chroma_db

# Server
MCP_SERVER_PORT=5000
STREAMLIT_PORT=8501
```

### Database Schema

**customers table:**
```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
email TEXT UNIQUE NOT NULL
phone TEXT
signup_date TEXT
account_status TEXT
account_type TEXT
total_orders INTEGER
lifetime_value REAL
```

**support_tickets table:**
```sql
id INTEGER PRIMARY KEY
customer_id INTEGER
title TEXT NOT NULL
description TEXT
status TEXT
created_date TEXT
resolved_date TEXT
category TEXT
priority TEXT
```

**orders table:**
```sql
id INTEGER PRIMARY KEY
customer_id INTEGER
order_date TEXT
amount REAL
status TEXT
items TEXT (JSON)
```

## 🤖 Adding Custom Policies

1. **Add document to backend/rag/docs/**
   ```bash
   cp your_policy.pdf backend/rag/docs/
   # or create a text file
   echo "Your policy content" > backend/rag/docs/my_policy.txt
   ```

2. **Reinitialize RAG pipeline**
   ```bash
   python -c "from backend.rag.rag_pipeline import setup_rag_pipeline; setup_rag_pipeline()"
   ```

3. **Query the new policy**
   - Ask questions about it in Streamlit UI
   - System will automatically retrieve relevant sections

## 🤖 Adding Custom Customers

Edit [backend/db/database.py](backend/db/database.py) `seed_sample_data()` function:

```python
# Add new customer
(id, name, email, phone, signup_date, status, type, orders, lifetime_value)
(6, "John Doe", "john@example.com", "+1-555-0106", "2024-01-01", "active", "premium", 10, 5000.00)
```

Then reinitialize:
```bash
python -c "from backend.db.database import init_database, seed_sample_data; init_database(); seed_sample_data()"
```

## 📡 MCP Tools Reference

### Policy Tools
- `query_policy(question)` - Query policies using RAG
- `get_policy_document(policy_name)` - Retrieve full policy
- `smart_query(question)` - Auto-route to appropriate agent

### Customer Tools
- `query_customer(question)` - Query customer data
- `get_customer_info(customer_name)` - Get customer profile
- `get_customer_tickets(customer_name)` - Get support tickets
- `search_customer_database(query)` - Search customers

### Admin Tools
- `health()` - Health check
- `execute_sql_query(sql_query)` - Execute SELECT queries

## 🐛 Troubleshooting

### Issue: "No documents found in docs directory"
**Solution:** Run initialization script:
```bash
python -c "from backend.rag.rag_pipeline import create_sample_policy_documents; create_sample_policy_documents()"
```

### Issue: Database connection errors
**Solution:** Reset database:
```bash
rm backend/db/customers.db
python -c "from backend.db.database import init_database, seed_sample_data; init_database(); seed_sample_data()"
```

### Issue: Streamlit import errors
**Solution:** Install required packages:
```bash
pip install -r backend/requirements.txt --upgrade
```

### Issue: MCP Server connection issues
**Solution:** Ensure FastMCP is properly installed:
```bash
pip install "mcp[cli]" --upgrade
```

## 📈 Extending the System

### Add New Agent Type

1. Create new agent class in [backend/agents/agents.py](backend/agents/agents.py):
```python
class MyAgent:
    def __init__(self):
        self.name = "MyAgent"
    
    def process_query(self, question: str) -> Dict[str, Any]:
        # Implementation
        return result
```

2. Register in `MultiAgentOrchestrator`:
```python
self.my_agent = MyAgent()
```

3. Add routing logic in `route_query()`:
```python
if "my_keyword" in question_lower:
    return self.my_agent.process_query(question)
```

4. Add MCP tool in [backend/mcp_server.py](backend/mcp_server.py):
```python
@mcp.tool()
def query_my_agent(question: str) -> str:
    result = orchestrator.my_agent.process_query(question)
    return json.dumps(result)
```

### Add New Data Source

1. Create data module in `backend/datasources/my_source.py`
2. Implement query functions
3. Integrate with agent in `backend/agents/agents.py`
4. Add MCP tool in `backend/mcp_server.py`

## 📝 Project Structure Details

### backend/agents/agents.py
- **PolicyAgent**: RAG-based policy answering
- **CustomerAgent**: SQL-based customer data retrieval
- **MultiAgentOrchestrator**: Query router and coordinator

### backend/db/database.py
- SQLite database management
- Customer CRUD operations
- Order and ticket management
- Search and query functions

### backend/rag/rag_pipeline.py
- Document loading and chunking
- Vector store (ChromaDB) management
- Similarity search for policy retrieval
- Policy summary extraction

### backend/mcp_server.py
- FastMCP server setup
- Tool definitions
- Agent integration
- Request handling

### frontend/app.py
- Streamlit UI components
- Query mode selection
- Response formatting
- Sample data display

## 🔐 Security Considerations

- ✅ SQL injection prevention: Only SELECT queries allowed
- ✅ Data isolation: Customer data accessed only through agents
- ✅ API authentication: MCP Server handles authorization
- ✅ Input validation: Query sanitization before execution
- ⚠️ TODO: Add rate limiting
- ⚠️ TODO: Add user authentication for Streamlit UI

## 📚 Further Reading

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🤝 Contributing

Feel free to extend this system with:
- Additional policy documents
- More customer data
- New agent types
- Alternative LLM/embedding models
- UI enhancements
- Performance optimizations

## 📄 License

This project is part of the TCS training initiative.

---

**Questions?** Review the inline code comments for detailed explanations of each component.
