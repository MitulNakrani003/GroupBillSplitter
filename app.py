import streamlit as st
import pandas as pd
from core.logic import (
    calculate_totals, 
    save_to_json, 
    create_bill_dataframe,
    load_participants,
    save_participants
)
from core.models import Bill

# --- Custom CSS for larger UI elements ---
st.markdown("""
<style>
    /* Increase base font size for the whole app */
    html, body, [class*="st-"], .st-emotion-cache-10trblm {
        font-size: 1.1rem;
    }
    
    /* Make headers larger */
    h1 {
        font-size: 2.8rem !important;
    }
    h2 {
        font-size: 2.2rem !important;
    }

    /* Increase padding and font size in text inputs and forms */
    .stTextInput input, .stNumberInput input {
        padding: 0.75rem;
        font-size: 1.1rem;
    }

    /* Increase padding and font size in buttons */
    .stButton button {
        padding: 0.75rem;
        font-size: 1.1rem;
        width: 100%;
    }

    /* Increase font size in the final dataframe */
    .stDataFrame {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


st.title("Bill Splitter Application")

# --- UI for Bill Title ---
bill_title = st.text_input("Enter Bill Title", value="New Bill")


# Initialize state
if 'bill' not in st.session_state:
    st.session_state.bill = Bill(description=bill_title)
# Update bill description if it changes
st.session_state.bill.description = bill_title

# Load participants from file on first run
if 'all_participants' not in st.session_state:
    st.session_state.all_participants = load_participants()
    # Also populate the bill object with these participants
    for name in st.session_state.all_participants:
        st.session_state.bill.add_participant(name)


# --- UI for Adding Participants ---
st.header("Add or Manage Participants")

# Define a callback function to handle adding a participant
def add_participant_callback():
    participant_name = st.session_state.participant_input
    if participant_name and participant_name not in st.session_state.all_participants:
        st.session_state.all_participants.append(participant_name)
        st.session_state.bill.add_participant(participant_name)
        save_participants(st.session_state.all_participants) # Save to file
    elif not participant_name:
        st.warning("Please enter a participant name.")
    else:
        st.warning(f"Participant '{participant_name}' already exists.")
    st.session_state.participant_input = ""

st.text_input(
    "Add New Participant", 
    key="participant_input", 
    on_change=add_participant_callback,
    placeholder="Enter name and press Enter"
)

# UI for Removing Participants
if st.session_state.all_participants:
    with st.expander("Manage Saved Participants"):
        participants_to_remove = st.multiselect(
            "Select participants to remove permanently",
            options=st.session_state.all_participants
        )
        if st.button("Remove Selected Participants"):
            if participants_to_remove:
                # Filter out the participants to remove
                st.session_state.all_participants = [
                    p for p in st.session_state.all_participants if p not in participants_to_remove
                ]
                # Save the updated list
                save_participants(st.session_state.all_participants)
                st.success("Removed selected participants.")
                st.rerun() # Rerun to update UI
            else:
                st.info("No participants selected to remove.")

# Display current participants
if st.session_state.all_participants:
    st.write("Current Participants:", ", ".join(sorted(st.session_state.all_participants)))


# --- UI for Adding Items ---
st.header("Add Items")
if st.session_state.all_participants:
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        item_price = st.number_input("Item Price", min_value=0.01, format="%.2f")
        selected_participants = st.multiselect(
            "Select Participants for this item",
            st.session_state.all_participants
        )
        submitted = st.form_submit_button("Add Item")
        if submitted:
            if item_name and item_price > 0 and selected_participants:
                st.session_state.bill.add_item(item_name, item_price, selected_participants)
                st.success(f"Added item: {item_name}")
            else:
                st.error("Please fill all fields and select at least one participant.")
else:
    st.warning("Please add at least one participant to start adding items.")

# --- UI for Removing Items ---
if st.session_state.bill.items:
    st.header("Remove an Item")
    item_names = [item['item_name'] for item in st.session_state.bill.items]
    item_to_remove = st.selectbox("Select item to remove", options=item_names)

    if st.button("Remove Selected Item"):
        if item_to_remove:
            st.session_state.bill.remove_item(item_to_remove)
            st.success(f"Removed item: {item_to_remove}")
            st.rerun() # Rerun to update the display immediately


# --- Display Totals and Save ---
# Use the dynamic title from the input field
st.header(st.session_state.bill.description)

if st.session_state.bill.items:
    # Create the detailed dataframe for display
    summary_df = create_bill_dataframe(st.session_state.bill)
    
    if not summary_df.empty:
        st.write("Detailed Bill Breakdown:")

        # --- Styling Logic ---
        def get_table_styler(df):
            # Get participant names for styling
            participant_columns = [p for p in df.columns if p != 'Total Price']

            # Define the styles using CSS
            styles = [
                # Thicker borders for the entire table and cells
                {'selector': 'th, td', 'props': 'border: 1.5px solid black;'},
                {'selector': 'table', 'props': 'border-collapse: collapse; border: 2px solid black;'},
                # Style for the 'Total Price' column header
                {'selector': 'th.col_heading.level0.col0', 'props': 'background-color: yellow;'},
                # Style for the 'Total Price' column cells with a lighter shade of yellow
                {'selector': 'td.col0', 'props': 'background-color: #ffffe0;'}, 
            ]

            # Dynamically create styles for each participant column header
            for i, col_name in enumerate(df.columns):
                if col_name in participant_columns:
                    styles.append({
                        'selector': f'th.col_heading.level0.col{i}',
                        'props': 'background-color: lightgreen;'
                    })
            
            # Custom formatter function
            def currency_formatter(val):
                if val == 0:
                    return '-'
                return f'${val:,.2f}'

            # Apply styles and formatting
            styler = df.style.format(currency_formatter, na_rep='-')
            styler.set_table_styles(styles)
            
            return styler

        # Apply the styling to the dataframe
        st.dataframe(get_table_styler(summary_df))

        if st.button("Save Results to JSON"):
            success, message = save_to_json(st.session_state.bill)
            if success:
                st.success(message)
                # Provide a download button for the JSON file
                with open("bill_summary.json", "r") as f:
                    st.download_button(
                        label="Download JSON",
                        data=f,
                        file_name="bill_summary.json",
                        mime="application/json"
                    )
            else:
                st.error(message)
else:
    st.info("No items added to the bill yet.")