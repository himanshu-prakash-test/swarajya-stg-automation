#!/bin/bash
set -o errexit

# Go to consultant-management directory
cd "$(dirname "$0")"

# Search for virtual environment in project roots
if [ -d "../../.venv" ]; then
    source ../../.venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export SWARAJYA_POPUP_TITLE="Consultant Management - Results"
export SWARAJYA_POPUP_HEADER="CONSULTANT MANAGEMENT AUTOMATION"

python3 -m pytest tests/test_consultant.py --headless -v -s "$@"
