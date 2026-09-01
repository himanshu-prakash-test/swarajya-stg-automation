# Consultant Management Automation

This folder contains the automation framework for the Consultant Management module.

## Setup
Dependencies are identical to the root project. If running independently:
```bash
pip install -r requirements.txt
```

## Running the Tests

To execute tests in headless mode (no browser UI visible, faster execution):
```bash
./run_headless.sh
```

To execute tests in headed mode (browser UI visible):
```bash
./run_headed.sh
```

## Test Data
Place your test cases and data in the `test_data/` directory.

## Output
Screenshots and execution logs will be saved automatically upon test failure or as designated in the test cases in the global `/screenshots` or `/reports` directory.
