"""
Root Pytest Configuration for login/emp-manager branch.
Ensures workspace root is in sys.path for shared module imports.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
