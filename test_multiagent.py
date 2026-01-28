#!/usr/bin/env python3
"""Test script for multi-agent chatbot"""

import os
os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/opt/sqlite/lib'

from dotenv import load_dotenv
load_dotenv()

from backend.db.database import init_database, seed_sample_data
init_database()
seed_sample_data()

from backend.chatbot import generate_answer

tests = [
    ("Who is Sarah Chen?", "Customer query with name"),
    ("Show Michael Davis account", "Customer query alternative phrasing"),
    ("What orders did Lisa Anderson place?", "Customer query about purchases"),
    ("Tell me about John Smith", "Customer query about person"),
    ("Return policy", "Policy query without customer keywords"),
    ("What are the shipping costs?", "Policy query alternative phrasing"),
    ("Ema Johnson profile", "Customer name only"),
]

print("\n" + "="*70)
print("MULTI-AGENT CHATBOT TEST")
print("="*70)

for i, (query, description) in enumerate(tests, 1):
    print(f"\nTEST {i}: {description}")
    print(f"Query: '{query}'")
    print("-" * 70)
    
    try:
        result = generate_answer(query)
        sources_list = [s['filename'] for s in result['sources']]
        
        print(f"Sources detected: {sources_list}")
        print(f"Answer preview: {result['answer'][:250]}...")
    except Exception as e:
        print(f"ERROR: {str(e)}")
