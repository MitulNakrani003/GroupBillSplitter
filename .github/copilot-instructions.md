# Copilot Instructions for BillSplitter

## Project Overview
A Streamlit-based bill splitting application that manages participants, groups, and calculates cost shares for items. Data persists to JSON files (`participants.json`, `groups.json`).

## Architecture

### Core Structure
```
app.py          # Streamlit UI, session state management, all user interactions
core/
  models.py     # Domain models: Bill, Participant, Item
  logic.py      # Business logic: calculations, JSON persistence, DataFrame creation
```

### Data Flow
1. **State Management**: All runtime state lives in `st.session_state` (bill, all_participants, groups)
2. **Persistence**: `participants.json` and `groups.json` store data between sessions
3. **Bill items** are stored as dicts: `{'item_name': str, 'price': float, 'participants': list}`

### Key Patterns

**Bill Cost Splitting** (`logic.py:create_bill_dataframe`):
- Uses cent-based arithmetic to avoid floating-point errors
- Remainder cents distributed to first N participants (fair rounding)
```python
price_in_cents = int(round(price * 100))
base_split_cents = price_in_cents // num_participants
remainder_cents = price_in_cents % num_participants
```

**Resource Paths** (`logic.py:resource_path`):
- Supports both development and PyInstaller bundled mode
- Use `resource_path()` for any file I/O to ensure compatibility

**Streamlit Form Callbacks**:
- Group selector uses `on_change` callback outside form to update `st.session_state.item_participants`
- Form submission triggers `st.rerun()` to refresh UI state

## Developer Commands

```bash
# Run development server
streamlit run app.py

# Run via bundler-compatible entry point
python run.py

# Build executable (PyInstaller)
pyinstaller BillSplitter.spec
```

## Code Conventions

- **Model mutations**: Always call `bill._recalculate_totals()` after modifying items
- **Participant changes**: Call `save_participants()` / `save_groups()` after any modification
- **DataFrame styling**: Currency formatting uses `${val:,.2f}` pattern with `-` for zero values
- **Sorted outputs**: Participants are sorted alphabetically when saved and displayed

## Common Modifications

**Adding a new Bill field**: Update `Bill` class in `models.py`, then handle in `create_bill_dataframe()` and `get_bill_as_json_string()` in `logic.py`

**Adding UI elements**: Use Streamlit forms with `clear_on_submit=True` for input sections; manage state via `st.session_state`

**Modifying cost calculation**: Edit `create_bill_dataframe()` — this is the source of truth for splits displayed and exported
