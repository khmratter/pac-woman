# conftest.py
import sys
import os

# Insert the project root (where conftest.py lives) at the front of sys.path
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
