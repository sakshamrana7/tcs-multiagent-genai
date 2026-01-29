# TCS Multi-Agent GenAI - Technology Stack & Design Decisions

## Executive Summary

This document outlines the technology choices for the TCS Multi-Agent GenAI system, including what each technology does, why it was chosen, benefits, and alternatives considered.

---

## 1. Large Language Model (LLM)

### Technology: Google Gemini 2.5-Flash

#### What It Is
Google Gemini 2.5-Flash is a lightweight, fast LLM from Google that provides:
- Fast inference (optimized for speed)
- Multimodal capabilities (text, images, code)
- Free tier quota (for development/testing)
- Production-grade quality
- 1M token context window

#### What It's Used For
- **Answer Generation**: Convert contextual data into natural language responses
- **Query Understanding**: Interpret user intent from natural language questions
- **Context Synthesis**: Combine customer DB data and policy documents into coherent answers
- **Source Attribution**: Maintain awareness of information sources while generating

#### Benefits
✅ **Free Tier Available**: 20 requests/day free (perfect for development)
✅ **Fast Inference**: "Flash" variant optimized for speed (2-3s response time)
✅ **Multimodal**: Can handle text, images, PDFs in future expansions
✅ **Large Context**: 1M token window allows long documents
✅ **High Quality**: Google's latest models (Gemini 2.x series)
✅ **Easy Integration**: LangChain provides wrapper for simple integration
✅ **No Infrastructure**: Cloud-based, no GPU needed locally

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|------------|--|
| **OpenAI GPT-4/3.5** | ❌ Paid only, $0.03-0.15 per query, no free tier |
| **Meta Llama 2** | ❌ Requires local GPU (expensive), slower inference, lower quality |
| **Anthropic Claude** | ❌ Paid only ($0.003-0.024 per query), no free tier |
| **Hugging Face Models** | ❌ Requires infrastructure, variable quality, maintenance overhead |
| **Open-source Mistral** | ❌ Lower quality than closed models, requires hosting |

#### Configuration
```python
ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,      # Balanced (0.0=deterministic, 1.0=creative)
    google_api_key="..."  # From AI Studio
)
```

#### Trade-offs
- **Pro**: Free tier, fast, good quality
- **Con**: Rate limited, requires internet connection, relies on Google's service

---

## 2. Vector Database

### Technology: ChromaDB

#### What It Is
ChromaDB is an open-source vector database designed for:
- Storing and retrieving embeddings (vectors)
- Semantic similarity search
- Document management
- Local-first architecture

#### What It's Used For
- **Document Indexing**: Convert policy documents into searchable vector embeddings
- **Semantic Search**: Find relevant documents based on meaning, not keywords
- **Persistence**: Store documents locally for offline access
- **RAG Foundation**: Core of Retrieval-Augmented Generation pipeline

#### Benefits
✅ **Open Source**: No licensing costs, full transparency
✅ **Local First**: Data stays on your machine, no cloud dependency
✅ **Lightweight**: Minimal dependencies, easy setup
✅ **Built-in Embeddings**: Comes with `all-MiniLM-L6-v2` model
✅ **Persistent Storage**: Auto-saves data to disk
✅ **Simple API**: Easy to use Python API
✅ **Python Native**: Perfect for Python-based ML/LLM workflows
✅ **Production Ready**: Used by major companies for RAG systems

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|------------|--|
| **Pinecone** | ❌ Cloud-only, $0.04/million vectors/month cost, vendor lock-in |
| **Weaviate** | ❌ Heavier setup, requires more infrastructure, overkill for this use case |
| **Milvus** | ❌ Requires separate server, more complex deployment |
| **Qdrant** | ❌ Cloud-first, additional deployment complexity |
| **FAISS** | ❌ No persistence, no HTTP API, harder to manage |
| **Elasticsearch** | ❌ Designed for full-text search, not semantic vectors, heavier |

#### Configuration
```python
# Local persistence at backend/rag/chroma_db/
client = chromadb.PersistentClient(path="backend/rag/chroma_db/")

# Create collection with default embeddings
collection = client.get_or_create_collection(
    name="policies_faqs",
    metadata={"hnsw:space": "cosine"}
)
```

#### Key Metrics
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Storage**: ~1MB per 100 documents
- **Search Speed**: < 200ms for similarity search
- **Scalability**: Handles up to millions of documents

#### Trade-offs
- **Pro**: Simple, local, no costs, fast
- **Con**: Single-machine limitation, no distributed setup out-of-box

---

## 3. Web Framework

### Technology: Streamlit

#### What It Is
Streamlit is a Python library for rapidly building web applications without JavaScript/CSS/HTML:
- Turns Python scripts into interactive web apps
- Hot-reloading for live development
- Component-based UI
- Built-in data visualization

#### What It's Used For
- **User Interface**: Web-based chat and search interface
- **File Upload**: Document upload functionality
- **Data Visualization**: Display customer profiles, search results
- **Multi-page App**: Different pages for different features
- **Session Management**: Maintain conversation state

#### Benefits
✅ **Zero Frontend Code**: Pure Python, no JavaScript needed
✅ **Rapid Development**: Build UIs 10x faster than traditional frameworks
✅ **Hot Reload**: See changes instantly while coding
✅ **Built-in Components**: Buttons, text inputs, file uploaders, etc.
✅ **Data Science Friendly**: Integrates with pandas, plotly, numpy
✅ **Free Hosting**: Deploy free on Streamlit Cloud
✅ **Session State**: Automatically manages user sessions
✅ **Mobile Responsive**: Works on phones, tablets, desktop

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|-----------|--|
| **Flask/Django** | ❌ Requires HTML/CSS/JavaScript knowledge, more boilerplate, slower development |
| **FastAPI** | ❌ API-first design, harder for interactive UI, more infrastructure |
| **Dash (Plotly)** | ❌ More verbose, steeper learning curve, slower development |
| **Gradio** | ❌ Limited to simple input/output, not suitable for complex multi-page apps |
| **Streamlit Cloud** | ✅ Perfect for this use case (chosen!) |

#### Implementation
```python
import streamlit as st

# Multi-page setup
page = st.sidebar.radio("Navigate", ["Search", "Profile", "Chat", "Upload"])

if page == "Chat":
    st.title("AI Chatbot")
    query = st.text_input("Ask a question:")
    if query:
        result = generate_answer(query)
        st.write(result["answer"])
        st.sidebar.write("Sources:", result["sources"])
```

#### Trade-offs
- **Pro**: Rapid development, Python-only, great for prototyping
- **Con**: Not suitable for complex enterprise applications, deployment slightly tricky

---

## 4. Relational Database

### Technology: SQLite

#### What It Is
SQLite is a file-based SQL database that:
- Stores structured data locally
- Requires no server
- ACID compliance
- Widely supported

#### What It's Used For
- **Customer Data**: Store customer profiles and information
- **Order History**: Maintain customer orders and transactions
- **Support Tickets**: Track customer support requests
- **Structured Queries**: SQL-based data retrieval

#### Benefits
✅ **Zero Setup**: Single file database, no server to run
✅ **No Dependencies**: Included with Python
✅ **ACID Compliant**: Data integrity guaranteed
✅ **SQL Standard**: Use standard SQL queries
✅ **Portable**: Single `.db` file, easy to backup
✅ **Production Ready**: Used by billions of devices
✅ **Free & Open Source**: SQLite in public domain
✅ **Good Performance**: Handles 100k-1M records easily

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|-----------|--|
| **PostgreSQL** | ❌ Requires server, more setup for development, overkill for current scale |
| **MongoDB** | ❌ Document DB (unstructured), not ideal for relational customer data |
| **MySQL** | ❌ Requires server, more complex setup than needed |
| **CSV Files** | ❌ No structured queries, poor for concurrent access, no ACID |
| **JSON Files** | ❌ Manual parsing, no querying capability, scales poorly |

#### Schema
```sql
-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    signup_date TEXT,
    account_status TEXT,
    total_orders INTEGER,
    lifetime_value REAL
)

-- Support tickets table
CREATE TABLE support_tickets (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT,
    created_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
```

#### Trade-offs
- **Pro**: Simple, no infrastructure, perfect for development
- **Con**: Single-user, not suitable for large-scale concurrent writes

---

## 5. Embeddings Model

### Technology: all-MiniLM-L6-v2 (Sentence Transformers)

#### What It Is
A lightweight transformer model that converts text to 384-dimensional vector embeddings:
- Trained on semantic similarity
- Optimized for speed and efficiency
- Pre-trained on massive text corpus

#### What It's Used For
- **Document Encoding**: Convert policy documents into vectors
- **Query Encoding**: Convert user queries into vectors
- **Similarity Matching**: Find semantically similar documents
- **RAG Foundation**: Enables semantic search vs keyword search

#### Benefits
✅ **Lightweight**: Only 80MB, runs on CPU
✅ **Fast**: Encodes text in milliseconds
✅ **High Quality**: MiniLM series shows excellent semantic understanding
✅ **Open Source**: Hugging Face model, free to use
✅ **Pre-trained**: Ready to use, no training needed
✅ **Deterministic**: Same input always produces same embedding
✅ **Built-in**: ChromaDB includes it by default

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|-----------|--|
| **OpenAI Text-Embedding-3** | ❌ Paid API, adds latency, vendor lock-in |
| **Cohere Embeddings** | ❌ API-based, requires keys, costs money |
| **BERT (base)** | ❌ Larger (340MB), slower, less optimized |
| **GPT-3 Embeddings** | ❌ Expensive, adds latency, overkill |
| **Random Embeddings** | ❌ No semantic meaning, search fails |

#### Specifications
- **Model Name**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Model Size**: 80MB
- **Speed**: ~1000 documents/second on CPU
- **Provider**: Hugging Face (Sentence Transformers)
- **License**: Apache 2.0

#### Trade-offs
- **Pro**: Local, fast, free, good quality
- **Con**: 384 dimensions (vs 1536 for OpenAI), slightly lower quality for specialized domains

---

## 6. ORM (Object-Relational Mapping)

### Technology: SQLAlchemy

#### What It Is
Python ORM that provides:
- Object-oriented database access
- Query abstraction
- Connection pooling
- Migration support

#### What It's Used For
- **Query Building**: Generate SQL programmatically
- **Type Mapping**: Python objects ↔ Database rows
- **Connection Management**: Handle database connections
- **Data Validation**: Ensure data types match schema

#### Benefits
✅ **SQL Agnostic**: Switch databases without code changes
✅ **Type Safe**: Python type hints for database operations
✅ **Flexible**: Raw SQL when needed, ORM when convenient
✅ **Industry Standard**: Used by most Python projects
✅ **Mature**: Stable, well-documented, large community

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|-----------|--|
| **Raw SQL** | ❌ Verbose, error-prone, SQL injection risks |
| **Django ORM** | ❌ Tied to Django framework, overkill for this project |
| **Tortoise ORM** | ❌ Async-only, adds complexity |
| **Peewee** | ❌ Smaller community, less flexible |

#### Current Implementation
```python
import sqlite3

# Direct SQL (simple for current project)
cursor.execute("SELECT * FROM customers WHERE name LIKE ?", (query,))
```

#### Future Upgrade Path
```python
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///customers.db')
Session = sessionmaker(bind=engine)
session = Session()

# ORM-based queries
customer = session.query(Customer).filter_by(name=name).first()
```

#### Trade-offs
- **Pro**: Scalable, type-safe, database-agnostic
- **Con**: Learning curve, overhead for simple queries

---

## 7. Python Web Request Library

### Technology: LangChain Integration (Python-based)

#### What It Is
Abstraction layer for LLM interactions:
- Unified interface for different LLMs
- Built-in prompt management
- Message history handling
- Chain composition

#### What It's Used For
- **LLM Abstraction**: Call Gemini without dealing with HTTP directly
- **Prompt Management**: Organize system and user prompts
- **Message Handling**: Manage conversation state
- **Error Handling**: Retry logic, timeout management

#### Benefits
✅ **Abstraction Layer**: Switch LLMs with one line of code
✅ **Best Practices**: Follows LLM API best practices
✅ **Tool Integration**: Built-in integrations with 100+ tools
✅ **Memory Management**: Handles long conversations
✅ **Active Development**: Constantly improved, large community
✅ **Chaining**: Build complex workflows easily

#### Why Chosen Over Alternatives

| Alternative | Why Not Chosen |
|-----------|--|
| **Direct HTTP (requests)** | ❌ More boilerplate, error handling, retry logic |
| **Official Google SDK** | ❌ Less flexible, harder to switch models |
| **Hugging Face Inference API** | ❌ Different API than Google, vendor-specific |

#### Implementation
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="..."
)

messages = [
    SystemMessage(content="You are a helpful assistant..."),
    HumanMessage(content="Customer data: ...\n\nQuestion: ...?")
]

response = llm.invoke(messages)
```

#### Trade-offs
- **Pro**: Abstraction, tool integration, best practices
- **Con**: Slight overhead, dependency on LangChain maintenance

---

## 8. Text Chunking

### Technology: LangChain RecursiveCharacterTextSplitter

#### What It Is
Algorithm for breaking long documents into semantic chunks:
- Respects natural boundaries (paragraphs, sentences)
- Maintains context overlap
- Configurable chunk size and overlap

#### What It's Used For
- **Document Preprocessing**: Break policies into searchable chunks
- **Context Preservation**: Maintain semantic meaning across chunks
- **Vector Efficiency**: Optimize embeddings for retrieval
- **Token Management**: Stay within LLM context limits

#### Benefits
✅ **Semantic Aware**: Respects document structure
✅ **Overlap Support**: Maintains context between chunks
✅ **Configurable**: Adjust size for different documents
✅ **Efficient**: Single pass through document
✅ **Standard Approach**: Industry best practice for RAG

#### Configuration
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 1000 characters per chunk
    chunk_overlap=200,    # 200 character overlap between chunks
    length_function=len,
    is_separator_regex=False
)

chunks = splitter.split_text(document)
```

#### Why This Configuration
- **1000 chars**: ~150-200 tokens (good for context windows)
- **200 overlap**: Maintains semantic continuity
- **Character-based**: More predictable than token-based for different file types

#### Trade-offs
- **Pro**: Semantic awareness, overlap for context
- **Con**: Slightly wasteful (same content stored twice due to overlap)

---

## 9. Environment Management

### Technology: Python-dotenv

#### What It Is
Library for loading environment variables from `.env` files:
- Secure credential management
- Development/production separation
- No hardcoded secrets

#### What It's Used For
- **API Keys**: Store Google Gemini API key securely
- **Configuration**: Database paths, model names
- **Secrets**: Never commit to version control

#### Benefits
✅ **Industry Standard**: Used in 99% of Python projects
✅ **Simple**: One-line setup
✅ **Secure**: Keep secrets out of code
✅ **Flexible**: Environment-specific configs
✅ **Git-safe**: Add `.env` to `.gitignore`

#### Implementation
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file
api_key = os.getenv("GOOGLE_API_KEY")
```

#### Example `.env` File
```bash
GOOGLE_API_KEY=AIzaSyBFsJ564KCvzSZyEdaIR0D0RBCpbYo0Q1M
DATABASE_URL=sqlite:///backend/db/customers.db
LOG_LEVEL=INFO
```

#### Trade-offs
- **Pro**: Simple, standard, secure
- **Con**: Must remember to create `.env` locally

---

## 10. Development Tools

### Technology: Git & GitHub

#### What It Is
Version control system and cloud repository:
- Track code changes
- Collaborate with team
- Maintain history
- Deploy from git

#### What It's Used For
- **Source Control**: Version all code changes
- **Collaboration**: Multiple developers working together
- **Backup**: Code safely stored in cloud
- **CI/CD**: Automated deployment from git

#### Benefits
✅ **Industry Standard**: Everyone uses Git
✅ **Distributed**: Full history on every machine
✅ **Branching**: Experiment safely with branches
✅ **Free**: GitHub free tier is generous
✅ **Integration**: Works with all tools (Streamlit, Docker, AWS, etc.)

---

## Complete Technology Stack Summary

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│                    (Streamlit)                          │
├─────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                    │
│              (Python + LangChain Framework)             │
├─────────────────────────────────────────────────────────┤
│  LLM Layer       │  Data Layer      │  Vector Layer     │
│  ────────────────┼──────────────────┼──────────────────│
│  Google Gemini   │  SQLite DB       │  ChromaDB        │
│  2.5-Flash       │  + SQLAlchemy    │  + MiniLM        │
│  (via LangChain) │                  │  Embeddings      │
└─────────────────────────────────────────────────────────┘
```

---

## Cost Analysis

### Total Cost of Operation

| Component | Cost | Notes |
|-----------|------|-------|
| **Google Gemini API** | $0/month | Free tier: 20 requests/day |
| **ChromaDB** | $0/month | Open source, self-hosted |
| **Streamlit** | $0/month | Open source (cloud hosting optional) |
| **SQLite** | $0/month | No license, single file |
| **Infrastructure** | $0/month | Runs on laptop/small server |
| **Domain Name** | $0-12/year | Optional, not required |
| **Hosting** | $0-10/month | Optional Streamlit Cloud or self-hosted |
| **────────────────** | **────────** | |
| **TOTAL (Minimal)** | **$0/month** | 100% free development |
| **TOTAL (Production)** | **$10-20/month** | With Streamlit Cloud hosting |

### Scaling Costs
- Free tier limited to 20 queries/day (Gemini)
- For production: ~$0.001 per query with Gemini API
- 1000 queries/day = ~$1/month

---

## Performance Characteristics

| Operation | Time | Bottleneck |
|-----------|------|------------|
| Customer Search | 50ms | SQLite query |
| Document Search | 300ms | Vector similarity search |
| LLM Response | 2-3s | API latency + generation |
| Total Query | 3-4s | LLM dominates |

---

## Scalability Roadmap

### Phase 1 (Current)
- Single machine, SQLite, ChromaDB local
- Suitable for: Development, demo, <100 daily users

### Phase 2 (Growth)
- PostgreSQL (replaces SQLite)
- Pinecone or Weaviate (replaces ChromaDB)
- Docker containerization
- Suitable for: 1000+ daily users

### Phase 3 (Production)
- Kubernetes orchestration
- Multi-model LLM strategy
- Distributed vector DB
- Advanced caching (Redis)
- Suitable for: 100k+ daily users

---

## Security Considerations

| Concern | Solution | Implementation |
|---------|----------|---|
| API Keys Exposed | Use `.env` files | Never commit to git |
| SQL Injection | Parameterized Queries | Use `?` placeholders |
| Vector DB Compromise | Local storage | Keep on secure server |
| LLM Prompt Injection | Input sanitization | Validate before LLM |
| Data Privacy | Encryption at rest | Consider for production |

---

## Conclusion

The chosen technology stack balances:
- **Simplicity**: Easy to understand and maintain
- **Cost**: 100% free for development
- **Performance**: Fast responses, minimal latency
- **Scalability**: Can grow from 0 to 1M+ users
- **Flexibility**: Can swap components as needed

This stack is ideal for **rapid prototyping, MVPs, and production deployment** with minimal infrastructure requirements.

