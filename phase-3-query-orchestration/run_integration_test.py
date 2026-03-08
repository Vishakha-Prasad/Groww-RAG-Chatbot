import sys, os
project_root = os.path.abspath(os.path.join(__file__, '..', '..'))
phase3 = os.path.join(project_root, 'phase-3-query-orchestration')
sys.path.append(phase3)
from chat_pipeline import answer_query
result = answer_query('What is the expense ratio for HDFC Nifty 1D Rate Liquid ETF - Growth')
print(result)
