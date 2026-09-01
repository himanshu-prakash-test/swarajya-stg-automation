#!/bin/zsh
set -o errexit
cd "$(dirname "$0")/../.."
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
export EMPLOYEE_UPDATE_WORKBOOK="${EMPLOYEE_UPDATE_WORKBOOK:-$PWD/update/emp_mgmt/test_data/Swarajya-Update-Employee-test-cases.xlsx}"
export SWARAJYA_POPUP_TITLE="Swarajya Employee Update - Results"
export SWARAJYA_POPUP_HEADER="SWARAJYA EMPLOYEE UPDATE AUTOMATION"
python3 -m pytest update/emp_mgmt/tests/test_employee_updates.py --headed -v -s "$@"

