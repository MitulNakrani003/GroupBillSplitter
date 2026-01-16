# AGENTS.md - BillSplitter

## Project Overview

A Streamlit-based bill splitting application that manages participants, groups, and calculates cost shares for items. Data persists to JSON files (`participants.json`, `groups.json`).

## Architecture

```
app.py              # Streamlit UI, session state management, all user interactions
run.py              # PyInstaller-compatible entry point
core/
  __init__.py       # Module initializer (empty)
  models.py         # Domain models: Bill, Participant, Item
  logic.py          # Business logic: calculations, JSON persistence, DataFrame creation
.streamlit/
  config.toml       # Streamlit theme configuration (light theme)
```

### Data Flow
1. **State Management**: All runtime state lives in `st.session_state` (bill, all_participants, groups)
2. **Persistence**: `participants.json` and `groups.json` store data between sessions
3. **Bill items** are stored as dicts: `{'item_name': str, 'price': float, 'participants': list}`

## Build/Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
streamlit run app.py

# Run via bundler-compatible entry point
python run.py

# Build macOS executable (PyInstaller)
pyinstaller BillSplitter.spec
```

### Testing

This project currently has no automated tests. When adding tests:

```bash
# Install pytest
pip install pytest

# Run all tests
pytest

# Run a single test file
pytest tests/test_logic.py

# Run a single test function
pytest tests/test_logic.py::test_calculate_totals

# Run with verbose output
pytest -v
```

## Code Style Guidelines

### Imports

Order imports as follows:
1. Standard library imports
2. Third-party imports (streamlit, pandas, reportlab)
3. Local imports (from core.logic, from core.models)

```python
import json
import sys
import os

import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter

from core.logic import calculate_totals, save_to_json
from core.models import Bill, Participant, Item
```

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters (soft limit)
- Use double quotes for strings in user-facing messages
- Use single quotes for internal strings and dict keys
- Use f-strings for string formatting: `f"${value:.2f}"`

### Types

- No static type hints are currently used in the codebase
- When adding types, use Python 3.9+ syntax: `list[str]` not `List[str]`
- Document function parameters and return types in docstrings

### Naming Conventions

- **Classes**: PascalCase (`Bill`, `Participant`, `Item`)
- **Functions/methods**: snake_case (`calculate_totals`, `add_item_to_bill`)
- **Variables**: snake_case (`item_name`, `price_in_cents`)
- **Constants**: UPPER_SNAKE_CASE (`PARTICIPANTS_FILE`, `GROUPS_FILE`)
- **Private methods**: prefix with underscore (`_recalculate_totals`)

### Error Handling

- Use try/except for file I/O operations
- Return empty defaults on error (empty list `[]` or dict `{}`)
- Catch specific exceptions: `FileNotFoundError`, `json.JSONDecodeError`

```python
def load_participants():
    try:
        with open(PARTICIPANTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
```

### Docstrings

Use simple one-line docstrings for straightforward functions:

```python
def load_participants():
    """Loads the list of participants from a JSON file."""
```

## Key Patterns

### Bill Cost Splitting (core/logic.py:55-88)

Uses cent-based arithmetic to avoid floating-point errors. Remainder cents are distributed to the first N participants:

```python
price_in_cents = int(round(price * 100))
base_split_cents = price_in_cents // num_participants
remainder_cents = price_in_cents % num_participants
```

### Resource Paths (core/logic.py:7-15)

Supports both development and PyInstaller bundled mode. Use `resource_path()` for any file I/O:

```python
from core.logic import resource_path
file_path = resource_path("participants.json")
```

### Streamlit State Management

- Initialize state with defaults in `if 'key' not in st.session_state`
- Use `st.rerun()` after state modifications that require UI refresh
- Form callbacks use `on_click` parameter for submit actions

### Model Mutations

Always call `bill._recalculate_totals()` after modifying items externally. The `add_item()` and `remove_item()` methods handle this automatically.

### Participant/Group Changes

Call `save_participants()` / `save_groups()` after any modification to persist changes.

### DataFrame Styling

Currency formatting uses `-` for zero values and `{val:.2f}` pattern for non-zero:

```python
def format_value(val):
    if val == 0:
        return "-"
    return f"{val:.2f}"
```

## Common Modifications

### Adding a New Bill Field

1. Update `Bill` class in `core/models.py`
2. Handle in `create_bill_dataframe()` in `core/logic.py`
3. Handle in `get_bill_as_json_string()` in `core/logic.py`

### Adding UI Elements

- Use Streamlit forms with `clear_on_submit=False` (manually clear via callbacks)
- Manage state via `st.session_state`
- Use `st.rerun()` to refresh UI after state changes

### Modifying Cost Calculation

Edit `create_bill_dataframe()` in `core/logic.py` - this is the source of truth for splits displayed and exported.

## Dependencies

Core dependencies (requirements.txt):
- `streamlit` - Web UI framework
- `pandas` - Data manipulation and DataFrame creation
- `reportlab` - PDF generation

Build dependencies:
- `pyinstaller` - For creating standalone executables

## Files to Never Commit

- `participants.json` and `groups.json` contain user data
- `bill_summary.json` is generated output
- `dist/` and `build/` directories (PyInstaller output)
- `__pycache__/` directories
