import streamlit as st
import pandas as pd
from core.logic import (
    calculate_totals, 
    save_to_json, 
    create_bill_dataframe,
    get_bill_as_json_string, # <-- Import the new function
    load_participants,
    save_participants,
    load_groups,
    save_groups
)
from core.models import Bill

# --- Page Configuration ---
st.set_page_config(
    page_title="Bill Splitter",
    page_icon="💰",
    layout="wide"
)

# --- Custom CSS for professional, clean UI ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Apply font globally */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .block-container {
        max-width: 90% !important;
        padding-top: 1.5rem !important;
    }
    
    /* Gradient background for main title */
    .main-title {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    
    .subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    /* Header styles */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #2d3748 !important;
    }
    h2 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.4rem;
        margin-top: 1.2rem !important;
    }
    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
    }
    
    /* Card-like sections - subtle styling */
    .stExpander {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 0.75rem;
    }
    
    .stExpander > div:first-child {
        border-radius: 12px 12px 0 0;
        background: #f7fafc;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .stExpander > div:first-child p {
        color: #4a5568 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* Styled text inputs - clean borders */
    .stTextInput > div > div > input {
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        background: #ffffff;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #a0aec0;
        box-shadow: 0 0 0 2px rgba(160, 174, 192, 0.2);
    }
    
    /* Styled number inputs */
    .stNumberInput > div > div > input {
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        background: #ffffff;
    }

    /* Primary buttons - softer colors */
    .stButton > button {
        background: #5a67d8;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(90, 103, 216, 0.2);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #4c51bf;
        box-shadow: 0 4px 8px rgba(90, 103, 216, 0.3);
    }
    
    /* Form submit button - teal accent */
    .stFormSubmitButton > button {
        background: #38a169;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
        width: 100%;
        box-shadow: 0 2px 4px rgba(56, 161, 105, 0.2);
    }
    
    .stFormSubmitButton > button:hover {
        background: #2f855a;
        box-shadow: 0 4px 8px rgba(56, 161, 105, 0.3);
    }

    /* Styled selectbox - subtle */
    .stSelectbox > div > div {
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #cbd5e0;
    }
    
    /* Styled multiselect - subtle tags */
    .stMultiSelect > div > div {
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
    }
    
    .stMultiSelect > div > div:hover {
        border-color: #cbd5e0;
    }
    
    /* Multiselect tags - soft pastel */
    .stMultiSelect > div > div > div > div {
        background: #edf2f7;
        color: #4a5568;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }

    /* Tab styling - clean and minimal */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f7fafc;
        padding: 0.4rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        color: #718096;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #4a5568;
        background: #edf2f7;
    }
    
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #2d3748 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Success/Error/Warning/Info messages - softer */
    .stSuccess {
        background: #f0fff4;
        border-radius: 8px;
        border-left: 3px solid #48bb78;
    }
    
    .stError {
        background: #fff5f5;
        border-radius: 8px;
        border-left: 3px solid #fc8181;
    }
    
    .stWarning {
        background: #fffff0;
        border-radius: 8px;
        border-left: 3px solid #ecc94b;
    }
    
    .stInfo {
        background: #ebf8ff;
        border-radius: 8px;
        border-left: 3px solid #63b3ed;
    }

    /* Download button - green accent */
    .stDownloadButton > button {
        background: #48bb78;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.25rem;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(72, 187, 120, 0.2);
    }
    
    .stDownloadButton > button:hover {
        background: #38a169;
        box-shadow: 0 4px 8px rgba(72, 187, 120, 0.3);
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    /* Form container - clean card */
    [data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    /* Metrics cards - minimal */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.75rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }
    
    /* Metric value styling */
    [data-testid="stMetricValue"] {
        color: #2d3748 !important;
    }

    /* Divider styling */
    hr {
        border-color: #e2e8f0;
        margin: 1rem 0;
    }

</style>
""", unsafe_allow_html=True)

# --- Main Title with gradient ---
st.markdown('<h1 class="main-title">💰 Bill Splitter</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Split bills fairly among friends with ease</p>', unsafe_allow_html=True)

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
tab1, tab2 = st.tabs(["📝 Bill Entry", "👥 Manage Participants & Groups"])


# --- Tab 1: Bill Entry ---
with tab1:
    # Create two columns for better layout
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        # --- UI for Bill Title ---
        st.markdown("### 📋 Bill Details")
        bill_title = st.text_input("Enter Bill Title", value=st.session_state.bill.description, placeholder="e.g., Dinner at Restaurant")
        st.session_state.bill.description = bill_title

        # --- UI for Adding Items ---
        st.markdown("### ➕ Add Items")
        if st.session_state.all_participants:
            # Initialize a state variable to hold the participants for the item being added
            if 'item_participants' not in st.session_state:
                st.session_state.item_participants = []
            
            # Initialize state to track if we need to reset the group selector
            if 'reset_group_selector' not in st.session_state:
                st.session_state.reset_group_selector = False

            # Callback function to update participants when a group is selected
            def on_group_select():
                group = st.session_state.group_selector
                if group and group != "— Select a group to pre-fill —":
                    st.session_state.item_participants = st.session_state.groups[group]
                else:
                    # If manual/no group is selected, clear the participants
                    st.session_state.item_participants = []

            # --- Group selection is now OUTSIDE the form ---
            group_options = ["— Select a group to pre-fill —"] + list(st.session_state.groups.keys())
            
            # Reset the group selector if flag is set
            default_index = 0
            if st.session_state.reset_group_selector:
                st.session_state.reset_group_selector = False
                # Force the selector to the default option
                if 'group_selector' in st.session_state:
                    del st.session_state.group_selector
            
            st.selectbox(
                "Quick Select a Group", 
                options=group_options, 
                key="group_selector",
                on_change=on_group_select
            )

            # --- The form now only contains the final inputs ---
            # Add clear_on_submit=True to the form
            with st.form("add_item_form", clear_on_submit=True):
                item_name = st.text_input("Item Name", placeholder="e.g., Pizza, Drinks")
                item_price = st.number_input("Item Price", min_value=0.01, format="%.2f")
                
                # The multiselect uses the state variable, which was set by the widget outside the form
                selected_participants = st.multiselect(
                    "Select Participants for this item",
                    st.session_state.all_participants,
                    default=st.session_state.item_participants
                )
                
                submitted = st.form_submit_button("➕ Add Item")
                if submitted:
                    if item_name and item_price > 0 and selected_participants:
                        st.session_state.bill.add_item(item_name, item_price, selected_participants)
                        # Clear the participants list for the next item
                        st.session_state.item_participants = []
                        # Set flag to reset the group selector on next rerun
                        st.session_state.reset_group_selector = True
                        st.success(f"✅ Added item: {item_name}")
                        st.rerun() # Rerun to refresh the display and reset the group selector
                    else:
                        st.error("Please fill all fields and select at least one participant.")
        else:
            st.warning("👋 Please add at least one participant in the 'Manage' tab to start adding items.")

        # --- UI for Removing Items ---
        if st.session_state.bill.items:
            st.markdown("### 🗑️ Remove an Item")
            item_names = [item['item_name'] for item in st.session_state.bill.items]
            item_to_remove = st.selectbox("Select item to remove", options=item_names)

            if st.button("🗑️ Remove Selected Item", key="remove_item_btn"):
                if item_to_remove:
                    st.session_state.bill.remove_item(item_to_remove)
                    st.success(f"✅ Removed item: {item_to_remove}")
                    st.rerun()

    with col_right:
        # --- Display Totals and Save ---
        st.markdown(f"### 📊 {st.session_state.bill.description}")
        if st.session_state.bill.items:
            summary_df = create_bill_dataframe(st.session_state.bill)
            if not summary_df.empty:
                st.markdown("**Detailed Bill Breakdown:**")
                def get_table_styler(df):
                    participant_columns = [p for p in df.columns if p != 'Total Price']
                    
                    # Define alternating row colors - subtle and clean
                    def row_colors(row):
                        row_idx = df.index.get_loc(row.name)
                        if row.name == 'Total':
                            # Total row - soft blue highlight
                            return ['background-color: #ebf8ff; font-weight: 600; color: #2c5282'] * len(row)
                        elif row_idx % 2 == 0:
                            return ['background-color: #ffffff; color: #2d3748'] * len(row)
                        else:
                            return ['background-color: #f7fafc; color: #2d3748'] * len(row)
                    
                    styles = [
                        # Clean, readable styling
                        {'selector': 'th, td', 
                        'props': [
                            ('font-size', '0.95rem'), 
                            ('color', '#2d3748'),
                            ('border', '1px solid #e2e8f0'),
                            ('padding', '12px 14px'),
                            ('font-weight', '500')
                        ]},
                        {'selector': 'table', 'props': [
                            ('border-collapse', 'collapse'), 
                            ('border', '1px solid #e2e8f0'),
                            ('border-radius', '8px'),
                            ('width', '100%'),
                            ('overflow', 'hidden')
                        ]},
                        # Soft blue header for Total Price column
                        {'selector': 'th.col_heading.level0.col0', 'props': [
                            ('background-color', '#edf2f7'),
                            ('color', '#4a5568'), 
                            ('font-weight', '600'),
                            ('font-size', '0.95rem'),
                            ('border-bottom', '2px solid #cbd5e0')
                        ]},
                        # Light gray for Total Price data cells
                        {'selector': 'td.col0', 'props': [('background-color', '#f7fafc'), ('color', '#2d3748'), ('font-weight', '600')]}, 
                        # Style index column (item names)
                        {'selector': 'th.row_heading', 'props': [
                            ('background-color', '#f7fafc'), 
                            ('color', '#4a5568'), 
                            ('font-weight', '600'),
                            ('font-size', '0.95rem')
                        ]},
                    ]
                    # Soft green headers for participant columns
                    for i, col_name in enumerate(df.columns):
                        if col_name in participant_columns:
                            styles.append({'selector': f'th.col_heading.level0.col{i}', 'props': [
                                ('background-color', '#f0fff4'),
                                ('color', '#276749'), 
                                ('font-weight', '600'),
                                ('font-size', '0.95rem'),
                                ('border-bottom', '2px solid #9ae6b4')
                            ]})
                    
                    def currency_formatter(val):
                        if val == 0: return '—'
                        return f'${val:,.2f}'
                    
                    styler = df.style.format(currency_formatter, na_rep='—')
                    styler.apply(row_colors, axis=1)
                    styler.set_table_styles(styles)
                    return styler
                
                # Calculate dynamic height based on number of rows
                num_rows = len(summary_df)
                row_height = 55  # Approximate height per row in pixels
                header_height = 65
                table_height = (num_rows * row_height) + header_height + 20  # Extra padding
                
                st.dataframe(get_table_styler(summary_df), use_container_width=True, height=table_height)
                
                # Show quick stats
                total_bill = summary_df.loc['Total', 'Total Price']
                num_items = len(st.session_state.bill.items)
                # Get participant columns (all columns except 'Total Price')
                all_participant_cols = [p for p in summary_df.columns if p != 'Total Price']
                num_people = len([p for p in all_participant_cols if summary_df.loc['Total', p] > 0])
                
                st.markdown("---")
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("💵 Total Bill", f"${total_bill:,.2f}")
                with stat_col2:
                    st.metric("🍽️ Items", num_items)
                with stat_col3:
                    st.metric("👥 People", num_people)

                # --- Updated Download Logic ---
                st.markdown("---")
                json_string = get_bill_as_json_string(st.session_state.bill)
                if json_string:
                    st.download_button(
                        label="📥 Download Bill as JSON",
                        data=json_string,
                        file_name=f"{st.session_state.bill.description.replace(' ', '_')}.json",
                        mime="application/json",
                    )
        else:
            st.info("📋 No items added to the bill yet. Add items from the left panel to see the breakdown here.")

# --- Tab 2: Manage Participants & Groups ---
with tab2:
    st.markdown("### ⚙️ Manage Your Team")
    
    col_participants, col_groups = st.columns([1, 1], gap="large")
    
    with col_participants:
        with st.expander("👤 Add or Remove Individual Participants", expanded=True):
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
                participants_to_remove = st.multiselect("Select participants to remove permanently", options=sorted(st.session_state.all_participants))
                if st.button("🗑️ Remove Selected Participants"):
                    if participants_to_remove:
                        st.session_state.all_participants = [p for p in st.session_state.all_participants if p not in participants_to_remove]
                        save_participants(st.session_state.all_participants)
                        st.success("✅ Removed selected participants.")
                        st.rerun()
                    else: st.info("No participants selected to remove.")

    with col_groups:
        with st.expander("👥 Create, Edit or Delete Groups", expanded=True):
            with st.form("create_group_form", clear_on_submit=True):
                st.markdown("**Create a New Group**")
                new_group_name = st.text_input("New Group Name", placeholder="e.g., Family, Work Team")
                new_group_members = st.multiselect("Select members for the new group", options=sorted(st.session_state.all_participants))
                submitted = st.form_submit_button("✨ Create Group")
                if submitted:
                    if new_group_name and new_group_members:
                        st.session_state.groups[new_group_name] = new_group_members
                        save_groups(st.session_state.groups)
                        st.success(f"✅ Group '{new_group_name}' created.")
                    else: st.warning("Please provide a group name and select at least one member.")
            
            # --- Edit Existing Groups ---
            if st.session_state.groups:
                st.markdown("---")
                st.markdown("**Edit an Existing Group**")
                group_to_edit = st.selectbox("Select group to edit", options=list(st.session_state.groups.keys()), key="group_to_edit_selector")
                
                if group_to_edit:
                    current_members = st.session_state.groups.get(group_to_edit, [])
                    updated_members = st.multiselect(
                        f"Edit members for '{group_to_edit}'",
                        options=sorted(st.session_state.all_participants),
                        default=current_members,
                        key="edit_group_members"
                    )
                    
                    if st.button("💾 Save Group Changes"):
                        if updated_members:
                            st.session_state.groups[group_to_edit] = updated_members
                            save_groups(st.session_state.groups)
                            st.success(f"✅ Group '{group_to_edit}' updated.")
                            st.rerun()
                        else:
                            st.warning("A group must have at least one member.")
                
                st.markdown("---")
                st.markdown("**Delete an Existing Group**")
                group_to_delete = st.selectbox("Select group to delete", options=list(st.session_state.groups.keys()), key="group_to_delete_selector")
                if st.button("🗑️ Delete Selected Group"):
                    if group_to_delete:
                        del st.session_state.groups[group_to_delete]
                        save_groups(st.session_state.groups)
                        st.success(f"✅ Group '{group_to_delete}' deleted.")
                        st.rerun()

    # Current Setup Summary
    st.markdown("---")
    st.markdown("### 📋 Current Setup Summary")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        if st.session_state.all_participants:
            st.markdown(f"""
            <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 3px solid #5a67d8;">
                <strong style="color: #4a5568;">👥 Current Participants ({len(st.session_state.all_participants)})</strong><br>
                <span style="color: #718096; font-size: 0.95rem;">{", ".join(sorted(st.session_state.all_participants))}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No participants added yet.")
    
    with summary_col2:
        if st.session_state.groups:
            groups_html = "<br>".join([f"<strong>{name}:</strong> {', '.join(members)}" for name, members in st.session_state.groups.items()])
            st.markdown(f"""
            <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 3px solid #48bb78;">
                <strong style="color: #4a5568;">🏷️ Available Groups ({len(st.session_state.groups)})</strong><br>
                <span style="color: #718096; font-size: 0.95rem;">{groups_html}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No groups created yet.")