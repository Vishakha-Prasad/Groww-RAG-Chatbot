import os
import sys
from pathlib import Path

# Add the project root to sys.path so we can find other modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "phase-3-query-orchestration"))
sys.path.append(str(PROJECT_ROOT / "phase-4-safety-eval"))
sys.path.append(str(PROJECT_ROOT / "phase-5-app-backend-frontend"))

# Import the FastAPI app from main.py
from main import app

# Vercel needs the app instance to be called 'app' or exported
# If you need to do any pre-initialization (like loading the index), you can do it here.
# However, main.py and chat_pipeline.py already handle this.
