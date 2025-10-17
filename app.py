import streamlit as st
import pandas as pd
from core.logic import (
    calculate_totals, 
    save_to_json, 
    create_bill_dataframe,
    load_participants,
    save_participants,
    load_groups,
    save_groups
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

# Initialize state (runs only once)
if 'bill' not in st.session_state:
    st.session_state.bill = Bill(description="New Bill")
if 'all_participants' not in st.session_state:
    st.session_state.all_participants = load_participants()
    for name in st.session_state.all_participants:
        st.session_state.bill.add_participant(name)
if 'groups' not in st.session_state:
    st.session_state.groups = load_groups()

# --- Define Tabs ---
tab1, tab2 = st.tabs(["Bill Entry", "Manage Participants & Groups"])


# --- Tab 1: Bill Entry ---
with tab1:
    # --- UI for Bill Title ---
    bill_title = st.text_input("Enter Bill Title", value=st.session_state.bill.description)
    st.session_state.bill.description = bill_title

    # --- UI for Adding Items ---
    st.header("Add Items")
    if st.session_state.all_participants:
        with st.form("add_item_form", clear_on_submit=True):
            item_name = st.text_input("Item Name")
            item_price = st.number_input("Item Price", min_value=0.01, format="%.2f")
            
            group_options = ["(Manual Selection)"] + list(st.session_state.groups.keys())
            selected_group = st.selectbox("Quick Select a Group", options=group_options)
            
            default_participants = []
            if selected_group and selected_group != "(Manual Selection)":
                default_participants = st.session_state.groups[selected_group]

            selected_participants = st.multiselect(
                "Select Participants for this item",
                st.session_state.all_participants,
                default=default_participants
            )
            submitted = st.form_submit_button("Add Item")
            if submitted:
                if item_name and item_price > 0 and selected_participants:
                    st.session_state.bill.add_item(item_name, item_price, selected_participants)
                    st.success(f"Added item: {item_name}")
                else:
                    st.error("Please fill all fields and select at least one participant.")
    else:
        st.warning("Please add at least one participant in the 'Manage' tab to start adding items.")

    # --- UI for Removing Items ---
    if st.session_state.bill.items:
        st.header("Remove an Item")
        item_names = [item['item_name'] for item in st.session_state.bill.items]
        item_to_remove = st.selectbox("Select item to remove", options=item_names)

        if st.button("Remove Selected Item"):
            if item_to_remove:
                st.session_state.bill.remove_item(item_to_remove)
                st.success(f"Removed item: {item_to_remove}")
                st.rerun()

    # --- Display Totals and Save ---
    st.header(st.session_state.bill.description)
    if st.session_state.bill.items:
        summary_df = create_bill_dataframe(st.session_state.bill)
        if not summary_df.empty:
            st.write("Detailed Bill Breakdown:")
            def get_table_styler(df):
                participant_columns = [p for p in df.columns if p != 'Total Price']
                styles = [
                    {'selector': 'th, td', 'props': 'border: 1.5px solid black;'},
                    {'selector': 'table', 'props': 'border-collapse: collapse; border: 2px solid black;'},
                    {'selector': 'th.col_heading.level0.col0', 'props': 'background-color: yellow;'},
                    {'selector': 'td.col0', 'props': 'background-color: #ffffe0;'}, 
                ]
                for i, col_name in enumerate(df.columns):
                    if col_name in participant_columns:
                        styles.append({'selector': f'th.col_heading.level0.col{i}', 'props': 'background-color: lightgreen;'})
                def currency_formatter(val):
                    if val == 0: return '-'
                    return f'${val:,.2f}'
                styler = df.style.format(currency_formatter, na_rep='-')
                styler.set_table_styles(styles)
                return styler
            st.dataframe(get_table_styler(summary_df))
            if st.button("Save Results to JSON"):
                success, message = save_to_json(st.session_state.bill)
                if success:
                    st.success(message)
                    with open("bill_summary.json", "r") as f:
                        st.download_button("Download JSON", f, "bill_summary.json", "application/json")
                else:
                    st.error(message)
    else:
        st.info("No items added to the bill yet.")

# --- Tab 2: Manage Participants & Groups ---
with tab2:
    st.header("Manage Participants & Groups")

    with st.expander("Add or Remove Individual Participants", expanded=True):
        def add_participant_callback():
            participant_name = st.session_state.participant_input
            if participant_name and participant_name not in st.session_state.all_participants:
                st.session_state.all_participants.append(participant_name)
                st.session_state.bill.add_participant(participant_name)
                save_participants(st.session_state.all_participants)
            elif not participant_name: st.warning("Please enter a participant name.")
            else: st.warning(f"Participant '{participant_name}' already exists.")
            st.session_state.participant_input = ""
        st.text_input("Add New Participant", key="participant_input", on_change=add_participant_callback, placeholder="Enter name and press Enter")
        if st.session_state.all_participants:
            participants_to_remove = st.multiselect("Select participants to remove permanently", options=st.session_state.all_participants)
            if st.button("Remove Selected Participants"):
                if participants_to_remove:
                    st.session_state.all_participants = [p for p in st.session_state.all_participants if p not in participants_to_remove]
                    save_participants(st.session_state.all_participants)
                    st.success("Removed selected participants.")
                    st.rerun()
                else: st.info("No participants selected to remove.")

    with st.expander("Create or Delete Groups", expanded=True):
        with st.form("create_group_form", clear_on_submit=True):
            st.subheader("Create a New Group")
            new_group_name = st.text_input("New Group Name")
            new_group_members = st.multiselect("Select members for the new group", options=sorted(st.session_state.all_participants))
            submitted = st.form_submit_button("Create Group")
            if submitted:
                if new_group_name and new_group_members:
                    st.session_state.groups[new_group_name] = new_group_members
                    save_groups(st.session_state.groups)
                    st.success(f"Group '{new_group_name}' created.")
                else: st.warning("Please provide a group name and select at least one member.")
        if st.session_state.groups:
            st.subheader("Delete an Existing Group")
            group_to_delete = st.selectbox("Select group to delete", options=list(st.session_state.groups.keys()))
            if st.button("Delete Selected Group"):
                if group_to_delete:
                    del st.session_state.groups[group_to_delete]
                    save_groups(st.session_state.groups)
                    st.success(f"Group '{group_to_delete}' deleted.")
                    st.rerun()

    st.header("Current Setup")
    if st.session_state.all_participants:
        st.write("Current Participants:", ", ".join(sorted(st.session_state.all_participants)))
    if st.session_state.groups:
        st.write("Available Groups:", ", ".join(st.session_state.groups.keys()))