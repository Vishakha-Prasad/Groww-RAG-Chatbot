import sys
from pathlib import Path

# Add orchestration dir to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "phase-3-query-orchestration"))

from llm_client import generate_answer_with_groq
from retriever import retrieve_top_k

q = "What is the purpose of the HDFC Multi Asset Allocation Fund?"
print(f"Query: {q}")
import traceback
try:
    retrieved = retrieve_top_k(q, k=1)
    context = [
        {
            "text": r.text, 
            "scheme_name": r.scheme_name, 
            "source_url": r.source_url, 
            "attribute_type": r.attribute_type
        } 
        for r in retrieved
    ]
    answer = generate_answer_with_groq(q, context)
    print(f"Answer: {answer}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
