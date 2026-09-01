#!/bin/bash
set -o errexit

# Go to project root
cd "$(dirname "$0")/.."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export SWARAJYA_POPUP_TITLE="Consultant Management - Results"
export SWARAJYA_POPUP_HEADER="CONSULTANT MANAGEMENT AUTOMATION"

python3 -m pytest create_consultant_mgmt/tests/test_consultant.py --headed -v -s "$@"
