import sys, os
# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))
from attribute_extractor import (
    _extract_exit_load,
    _extract_min_sip,
    _extract_min_lumpsum,
    _extract_lock_in,
    _extract_riskometer,
    _extract_benchmark,
    _extract_statement_download,
)
from retriever import RetrievedChunk

def make_chunk(text):
    return RetrievedChunk(
        text=text,
        scheme_id="dummy",
        scheme_name="Dummy Scheme",
        attribute_type="",
        source_url="https://example.com",
        score=1.0,
    )

samples = [
    ("Exit Load: 0.5%", _extract_exit_load),
    ("Exit Load - 1%", _extract_exit_load),
    ("Exit Load 2%", _extract_exit_load),
    ("Minimum SIP Investment is set to ₹100", _extract_min_sip),
    ("Min. for SIP ₹200", _extract_min_sip),
    ("SIP ₹300", _extract_min_sip),
    ("Minimum Lumpsum Investment is set to ₹500", _extract_min_lumpsum),
    ("Min. for 1st investment ₹600", _extract_min_lumpsum),
    ("Lumpsum ₹700", _extract_min_lumpsum),
    ("5Y Lock-in", _extract_lock_in),
    ("Lock-in period: 3Y", _extract_lock_in),
    ("lock-in 2Y", _extract_lock_in),
    ("Very High Risk", _extract_riskometer),
    ("Medium risk", _extract_riskometer),
    ("Benchmark Nifty 1D Rate TRI", _extract_benchmark),
    ("Fund benchmark NIFTY 50 Total Return Index", _extract_benchmark),
    ("Benchmark: NIFTY 100", _extract_benchmark),
    ("You can download statements from Groww via the app.", _extract_statement_download),
]

for txt, func in samples:
    result = func([make_chunk(txt)])
    print(f"Input: {txt}\nOutput: {result}\n---")
