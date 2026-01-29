# TCS Multi-Agent GenAI System - Architecture & Data Flow

## System Overview

The TCS Multi-Agent GenAI system is a sophisticated customer support platform that intelligently routes queries to appropriate data sources (customer database or policy documents) and generates contextual answers using LLM technology.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER QUERY (Frontend/API)                          │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │  Frontend: app_simple.py        │
                    │  (Streamlit Web Interface)      │
                    └────────┬──────────────────────┘
                             │
                             ▼
          ┌──────────────────────────────────────────┐
          │   Backend: chatbot.py                    │
          │   generate_answer(query)                 │
          └──────┬─────────────────────────┬────────┘
                 │                         │
     ┌───────────┴──────────┐    ┌────────┴──────────────┐
     │                      │    │                       │
     ▼                      ▼    ▼                       ▼
┌──────────────────┐ ┌────────────────────┐ ┌─────────────────────┐
│ Query Analysis   │ │ Customer Name      │ │ Keyword Detection   │
│ Module           │ │ Detection          │ │ (policy/return etc) │
└────┬─────────────┘ └─────┬──────────────┘ └────────┬────────────┘
     │                     │                        │
     │  Fetch all          │  Match against         │  Check for
     │  customer names     │  database              │  policy keywords
     │  from DB            │                        │
     └─────────┬───────────┴────────────┬───────────┘
               │                        │
               ▼                        ▼
    ┌──────────────────────────────────────────────┐
    │     Route Decision Logic                     │
    │                                              │
    │  if customer_name_found:                     │
    │      → Query Customer Database               │
    │  if policy_keywords_found:                   │
    │      → Search RAG/Policy Documents           │
    │  if both: → Combine both sources             │
    │  if neither: → Try customer DB first         │
    └─────────┬──────────────────────┬─────────────┘
              │                      │
     ┌────────▼──────────┐  ┌───────▼──────────────┐
     │                   │  │                      │
     ▼                   ▼  ▼                      ▼
┌────────────────┐ ┌───────────────────────────────────┐
│ Customer DB    │ │ RAG Pipeline (ChromaDB)           │
│ (SQLite)       │ │ - Vector Embeddings               │
│                │ │ - Document Search                 │
│ Tables:        │ │ - Similarity Matching             │
│ • customers    │ │                                   │
│ • orders       │ │ Collection: policies_faqs         │
│ • tickets      │ │                                   │
└────┬───────────┘ └─────┬──────────────────────────────┘
     │                   │
     │  Customer Info    │  Policy Content
     │  • Profile        │  + Relevance Score
     │  • Support        │
     │    Tickets        │
     │                   │
     └─────────┬─────────┘
               │
               ▼
    ┌────────────────────────────────┐
    │ Context Aggregation            │
    │                                │
    │ Combine:                       │
    │ • Customer Data                │
    │ • Policy Documents             │
    │ • Relevance Scores             │
    │ • Source Attribution           │
    └────────┬──────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ LLM Processing                 │
    │ (Google Gemini 2.5-Flash)      │
    │                                │
    │ Input:                         │
    │  • System Prompt               │
    │  • Context (DB + Docs)         │
    │  • User Query                  │
    │                                │
    │ Output:                        │
    │  • Generated Answer            │
    │  • Source Attribution          │
    └────────┬──────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ Post-Processing                │
    │                                │
    │ • Strip inline citations       │
    │ • Format source metadata       │
    │ • Clean output                 │
    └────────┬──────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Final Response                             │
│  {                                          │
│    "answer": "...",                         │
│    "sources": [...],                        │
│    "has_context": true/false,               │
│    "query": "..."                           │
│  }                                          │
└────────┬────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────┐
    │  Frontend Display       │
    │  (Streamlit UI)         │
    │  • Show Answer          │
    │  • Display Sources      │
    │  • Confidence Metrics   │
    └─────────────────────────┘
```

---

## Component Details

### 1. **Frontend Layer** (`frontend/app_simple.py`)

**Purpose**: Web interface for user interaction

**Pages/Endpoints**:
- **Search Customers** - Query customer database by name/email
- **Customer Profile** - View detailed customer information
- **Support Tickets** - List and manage customer support tickets
- **AI Chatbot** - Main multi-agent query interface
- **Document Search** - Search uploaded policy documents
- **Upload Documents** - Add new policy/FAQ documents

**Technology**: Streamlit (Python web framework)

---

### 2. **Core Chatbot Module** (`backend/chatbot.py`)

#### Main Function: `generate_answer(query, llm=None, n_results=5, collection_name="policies_faqs")`

**Input Parameters**:
- `query`: User's natural language question
- `llm`: ChatGoogleGenerativeAI instance (optional)
- `n_results`: Number of document chunks to retrieve
- `collection_name`: ChromaDB collection to search

**Processing Steps**:

1. **Query Type Detection**
   ```python
   # Fetch all customer names from database
   all_customer_names = [(name, name.lower()) for cust in search_customers("")]
   
   # Check if any customer names mentioned
   mentioned_customer_data = [...]
   ```

2. **Context Retrieval**
   - **Customer Path**: If names detected
     - `search_customers(name)` → Get customer record
     - `get_customer_profile(customer_id)` → Get detailed info
     - `get_customer_support_tickets(customer_id)` → Get tickets
   
   - **Policy Path**: If policy keywords detected
     - `search_documents(collection_name, query)` → Vector search
     - Retrieve relevant chunks with similarity scores

3. **Context Aggregation**
   - Combine results from both sources (if applicable)
   - Format with source attribution
   - Add relevance percentages

4. **LLM Invocation**
   ```python
   messages = [
       SystemMessage(content=system_prompt),
       HumanMessage(content=user_prompt_with_context)
   ]
   response = llm.invoke(messages)
   ```

5. **Post-Processing**
   - Strip inline citation markers (e.g., "[Source 1]")
   - Format final answer
   - Return with metadata

**Output**:
```python
{
    "answer": "...",  # Clean generated answer
    "sources": [...], # List of sources with relevance
    "has_context": True/False,
    "query": "original query"
}
```

---

### 3. **Database Layer** (`backend/db/database.py`)

**Database**: SQLite (`backend/db/customers.db`)

**Schema**:

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    signup_date TEXT,
    account_status TEXT,
    account_type TEXT,
    total_orders INTEGER,
    lifetime_value REAL
)

CREATE TABLE support_tickets (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT,
    created_date TEXT,
    resolved_date TEXT,
    category TEXT,
    priority TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
```

**Key Functions**:

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `init_database()` | Create tables | None | None |
| `seed_sample_data()` | Populate with 5 sample customers | None | None |
| `search_customers(query)` | Find customers by name/email/phone | string | List[Dict] |
| `get_customer_profile(customer_id)` | Get customer details | int | Dict |
| `get_customer_support_tickets(customer_id)` | Get all tickets for customer | int | List[Dict] |
| `query_database(sql_query)` | Execute custom SQL | string | List[Dict] |

**Sample Data**:
- Ema Johnson (ema.johnson@email.com)
- John Smith (john.smith@email.com)
- Sarah Chen (sarah.chen@email.com)
- Michael Davis (michael.d@email.com)
- Lisa Anderson (lisa.anderson@email.com)

---

### 4. **RAG Pipeline** (`backend/rag/rag_pipeline.py`)

**Purpose**: Document management and semantic search

**Key Components**:

#### ChromaDB Collection
- **Location**: `backend/rag/chroma_db/` (persistent storage)
- **Embedding Model**: `all-MiniLM-L6-v2` (384-dimensional vectors)
- **Collection Name**: `policies_faqs`

#### Document Processing

```
Raw Document
    ↓
Text Splitting (1000 chars, 200 overlap)
    ↓
Embedding Generation
    ↓
Vector Storage in ChromaDB
    ↓
Semantic Similarity Search
```

#### Key Functions**:

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `create_collection(name)` | Create vector collection | string | Collection object |
| `add_documents(docs, metadata, collection)` | Add docs to vector store | docs, metadata | None |
| `search_documents(collection, query, n_results)` | Semantic search | collection, query, int | List[{content, metadata, similarity}] |
| `delete_collection(name)` | Remove collection | string | None |
| `clear_collection(name)` | Empty collection | string | None |
| `get_collection_info(name)` | Get collection stats | string | Dict |

---

### 5. **LLM Integration** (`langchain_google_genai`)

**Model**: `gemini-2.5-flash`

**Configuration**:
```python
ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,  # Balanced creativity
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

**System Prompt**:
```
You are a knowledgeable multi-agent customer support assistant for TCS.
You have access to:
1. Customer database (profiles, orders, support tickets)
2. Company policies, FAQs, and guidelines

Your role is to answer questions using the provided context from both sources.
Always be helpful, accurate, and professional.
If information comes from customer data, acknowledge it clearly.
If information comes from policies, cite the policy source when relevant.
```

---

## API Endpoints (if REST API added)

### POST `/api/query`
**Request**:
```json
{
  "query": "Who is Sarah Chen and what is your return policy?"
}
```

**Response**:
```json
{
  "answer": "Sarah Chen is a valued customer with...",
  "sources": [
    {
      "id": 1,
      "filename": "customer_database",
      "relevance": "100%",
      "type": "customer_data"
    },
    {
      "id": 2,
      "filename": "sample_policy",
      "relevance": "95%",
      "type": "document"
    }
  ],
  "has_context": true,
  "query": "Who is Sarah Chen..."
}
```

### GET `/api/customers`
**Response**:
```json
{
  "customers": [
    {
      "id": 1,
      "name": "Ema Johnson",
      "email": "ema.johnson@email.com",
      "account_status": "active"
    }
  ]
}
```

### GET `/api/customers/{id}/profile`
**Response**:
```json
{
  "id": 1,
  "name": "Ema Johnson",
  "email": "ema.johnson@email.com",
  "phone": "555-1234",
  "address": "123 Main St",
  "account_status": "active"
}
```

### GET `/api/customers/{id}/tickets`
**Response**:
```json
{
  "tickets": [
    {
      "id": 1,
      "title": "Order issue",
      "status": "open",
      "priority": "high"
    }
  ]
}
```

### POST `/api/documents/upload`
**Request**: Multipart form with file upload
**Response**: 
```json
{
  "success": true,
  "file": "policy.pdf",
  "chunks_created": 15,
  "message": "Document uploaded and indexed"
}
```

### POST `/api/documents/search`
**Request**:
```json
{
  "query": "What is the refund policy?",
  "n_results": 5
}
```

**Response**:
```json
{
  "results": [
    {
      "content": "30-day money-back guarantee...",
      "similarity": 0.92,
      "source": "sample_policy.txt"
    }
  ]
}
```

---

## Query Routing Logic

```python
def route_query(query):
    """
    Intelligent routing decision based on query content
    """
    
    # Step 1: Check for mentioned customer names (dynamic)
    customer_names = get_all_customer_names_from_db()
    mentioned_names = [name for name in customer_names 
                      if name.lower() in query.lower()]
    
    # Step 2: Check for policy keywords
    policy_keywords = ["policy", "refund", "return", "shipping", ...]
    has_policy_keywords = any(kw in query.lower() 
                             for kw in policy_keywords)
    
    # Step 3: Routing Decision
    if mentioned_names and has_policy_keywords:
        return ROUTE_BOTH  # Combine customer + policy data
    elif mentioned_names:
        return ROUTE_CUSTOMER  # Customer database only
    elif has_policy_keywords:
        return ROUTE_POLICY  # Policy documents only
    else:
        return ROUTE_BOTH  # Try customer first, then policy
```

---

## Example Query Flows

### Example 1: Pure Customer Query
```
User Query: "Who is Ema Johnson?"
    ↓
Route Decision: Customer name detected → ROUTE_CUSTOMER
    ↓
Database: search_customers("Ema") 
    ↓
Context: Ema's profile, 2 support tickets
    ↓
LLM: Generate answer from customer data
    ↓
Output: "Ema Johnson is a customer with..."
Sources: ["customer_database"]
```

### Example 2: Pure Policy Query
```
User Query: "What are the shipping costs?"
    ↓
Route Decision: Policy keywords detected → ROUTE_POLICY
    ↓
RAG: search_documents("shipping costs")
    ↓
Context: 3 relevant document chunks (92-87% similarity)
    ↓
LLM: Generate answer from policy documents
    ↓
Output: "Standard Shipping: $9.99..."
Sources: ["sample_policy.txt" (92%), "sample_policy.txt" (90%), ...]
```

### Example 3: Hybrid Query
```
User Query: "Show Sarah Chen's profile and refund policy"
    ↓
Route Decision: Name + Policy keywords → ROUTE_BOTH
    ↓
Database: search_customers("Sarah")
    RAG: search_documents("refund policy")
    ↓
Context: Sarah's profile + 3 policy chunks
    ↓
LLM: Generate unified answer
    ↓
Output: "Sarah Chen is... Our refund policy is..."
Sources: ["customer_database", "sample_policy.txt" (94%)]
```

---

## Error Handling

### No Context Found
```python
if not all_context:
    return {
        "answer": "I couldn't find relevant information...",
        "sources": [],
        "has_context": False
    }
```

### Database Connection Error
```python
try:
    customer_results = search_customers(query)
except Exception as e:
    # Continue with policy search
    log_error(e)
    customer_context = ""
```

### API Key Missing
```python
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY not set. Set in .env file."
    )
```

---

## Deployment Considerations

1. **Environment Variables**
   - `GOOGLE_API_KEY`: Gemini API key from Google AI Studio
   - `DYLD_LIBRARY_PATH`: SQLite library path (macOS)

2. **Database Initialization**
   ```bash
   python -c "from backend.db.database import init_database, seed_sample_data; \
              init_database(); seed_sample_data()"
   ```

3. **Running the System**
   ```bash
   # Test mode
   DYLD_LIBRARY_PATH=/usr/local/opt/sqlite/lib python test_multiagent.py
   
   # Web UI (requires Streamlit)
   streamlit run frontend/app_simple.py
   ```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Customer Search | < 50ms |
| Document Search | 200-500ms (vector similarity) |
| LLM Response | 2-5s (including API latency) |
| Total Query Time | 3-6s |
| ChromaDB Size | ~5MB (for sample policies) |
| Database Size | ~100KB (5 customers + tickets) |

---

## Security Notes

1. **API Key**: Never commit `.env` to repository
2. **Database**: SQLite suitable for development; use PostgreSQL for production
3. **Input Validation**: LLM receives sanitized queries
4. **Source Attribution**: All sources traced back to original documents
5. **Rate Limiting**: Implement at API gateway level for production

