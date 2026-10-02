import os
import sys

# Tests must never reach the real Gemini API, whatever is in the local .env.
os.environ['GEMINI_API_KEY'] = ''
os.environ.pop('ALLOWED_ORIGINS', None)
os.environ.pop('ENABLE_DEBUG_PAGE', None)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
