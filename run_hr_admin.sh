#!/bin/bash
set -e
source venv/bin/activate
pytest tests/test_hr_admin.py --headed -v -s
