import json
import pandas as pd
import sys
import os
from .models import Bill, Item

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

PARTICIPANTS_FILE = resource_path("participants.json")
GROUPS_FILE = resource_path("groups.json")

def load_participants():
    """Loads the list of participants from a JSON file."""
    try:
        with open(PARTICIPANTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_participants(participants):
    """Saves the list of participants to a JSON file."""
    with open(PARTICIPANTS_FILE, 'w') as f:
        json.dump(sorted(participants), f, indent=4)

def load_groups():
    """Loads participant groups from a JSON file."""
    try:
        with open(GROUPS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_groups(groups):
    """Saves participant groups to a JSON file."""
    with open(GROUPS_FILE, 'w') as f:
        json.dump(groups, f, indent=4)

def add_item_to_bill(bill: Bill, item_name: str, price: float, participant_names: list):
    """Adds an item to the bill and splits the cost."""
    item = Item(name=item_name, price=price, participants=participant_names)
    bill.add_item(item)

def calculate_totals(bill: Bill):
    """Returns the total amount due for each participant."""
    return bill.get_totals()

def create_bill_dataframe(bill: Bill):
    """Creates a pandas DataFrame from the bill data in the desired format."""
    all_participant_names = sorted(list(bill.participants.keys()))
    item_data = {item['item_name']: item for item in bill.items}
    item_names = list(item_data.keys())
    
    # Create DataFrame with item names as index
    df = pd.DataFrame(0.0, index=item_names, columns=all_participant_names)

    # Insert the 'Total Price' column at the beginning
    df.insert(0, 'Total Price', [item_data[name]['price'] for name in item_names])

    # Populate item costs for each participant
    for item_name, item in item_data.items():
        price = item['price']
        participants = item['participants']
        if participants:
            num_participants = len(participants)
            # Calculate split in cents to avoid floating point errors and handle remainder
            price_in_cents = int(round(price * 100))
            base_split_cents = price_in_cents // num_participants
            remainder_cents = price_in_cents % num_participants

            for i, p_name in enumerate(participants):
                if p_name in df.columns:
                    # Add one cent from the remainder to the first few participants
                    extra_cent = 1 if i < remainder_cents else 0
                    split_amount = (base_split_cents + extra_cent) / 100.0
                    df.loc[item_name, p_name] = split_amount

    # Add 'Total' row at the end
    df.loc['Total'] = df.sum()
    # The 'Total' for the 'Total Price' column is the sum of that column
    df.loc['Total', 'Total Price'] = df['Total Price'].iloc[:-1].sum()

    return df

def get_bill_as_json_string(bill: Bill):
    """Generates the bill summary as a JSON formatted string."""
    try:
        df = create_bill_dataframe(bill)
        output_data = {
            "bill_title": bill.description,
            "summary_table": df.to_dict(orient='index')
        }
        return json.dumps(output_data, indent=4)
    except Exception as e:
        return None


def save_to_json(bill: Bill, filename="bill_summary.json"):
    """Saves the bill title and summary dataframe to a JSON file."""
    try:
        df = create_bill_dataframe(bill)
        
        output_data = {
            "bill_title": bill.description,
            "summary_table": df.to_dict(orient='index')
        }

        # Use the resource_path for the output file as well
        output_path = resource_path(filename)
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=4)
            
        return True, f"Data saved to {output_path}"
    except Exception as e:
        return False, f"Error saving to JSON: {e}"