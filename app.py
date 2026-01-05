import streamlit as st
import pandas as pd
from core.logic import (
    calculate_totals, 
    save_to_json, 
    create_bill_dataframe,
    get_bill_as_json_string,
    load_participants,
    save_participants,
    load_groups,
    save_groups
)
from core.models import Bill
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
        font-size: 18px !important; /* Global font size increase */
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
        font-size: 3.5rem !important; /* Increased */
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.3rem !important; /* Increased */
        margin-bottom: 2rem;
    }

    /* Header styles */
    h1 {
        font-size: 3rem !important; /* Increased */
        font-weight: 700 !important;
        color: #2d3748 !important;
    }
    h2 {
        font-size: 2rem !important; /* Increased */
        font-weight: 600 !important;
        color: #4a5568 !important;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem !important;
    }
    h3 {
        font-size: 1.5rem !important; /* Increased */
        font-weight: 600 !important;
        color: #4a5568 !important;
    }
    
    /* Card-like sections - subtle styling */
    .stExpander {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }
    
    .stExpander > div:first-child {
        border-radius: 12px 12px 0 0;
        background: #f7fafc;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .stExpander > div:first-child p {
        color: #4a5568 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important; /* Increased */
    }

    /* Styled text inputs - clean borders */
    .stTextInput > div > div > input {
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.8rem 1.2rem; /* Increased padding */
        font-size: 1.1rem !important; /* Increased */
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
        padding: 0.8rem 1.2rem;
        font-size: 1.1rem !important;
        background: #ffffff;
    }

    /* Primary buttons - softer colors */
    .stButton > button {
        background: #5a67d8;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem; /* Increased */
        font-size: 1.1rem !important; /* Increased */
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
        padding: 0.8rem 1.5rem; /* Increased */
        font-size: 1.1rem !important; /* Increased */
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
        font-size: 1rem !important; /* Added */
    }

    /* Tab styling - clean and minimal */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #f7fafc;
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.8rem 2rem; /* Increased */
        font-weight: 500;
        color: #718096;
        background: transparent;
        font-size: 1.1rem !important; /* Increased */
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
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        font-size: 1.1rem !important;
    }
    .stSuccess { background: #f0fff4; border-left: 3px solid #48bb78; }
    .stError { background: #fff5f5; border-left: 3px solid #fc8181; }
    .stWarning { background: #fffff0; border-left: 3px solid #ecc94b; }
    .stInfo { background: #ebf8ff; border-left: 3px solid #63b3ed; }

    /* Download button - green accent */
    .stDownloadButton > button {
        background: #48bb78;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 1.5rem; /* Increased */
        font-size: 1.1rem !important; /* Increased */
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
        font-size: 1.1rem !important; /* Try to hit outer container too */
    }

    /* Form container - clean card */
    [data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem; /* Increased */
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    /* Metrics cards - minimal */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem; /* Increased */
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }
    
    /* Metric value styling */
    [data-testid="stMetricValue"] {
        color: #2d3748 !important;
        font-size: 2.5rem !important; /* Explicitly large */
    }

    /* Divider styling */
    hr {
        border-color: #e2e8f0;
        margin: 1.5rem 0;
    }

</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def generate_pdf(bill):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = styles['Title']
    title_style.fontName = 'Helvetica-Bold'
    elements.append(Paragraph(f"Bill: {bill.description}", title_style))
    elements.append(Spacer(1, 12))

    # Data for table
    data = [['Item', 'Price', 'Participants']]
    for item in bill.items:
        data.append([
            item['item_name'],
            f"${item['price']:.2f}",
            ", ".join(item['participants'])
        ])
    
    # Create Table
    if len(data) > 1:
        t = Table(data, colWidths=[200, 100, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No items in this bill.", styles['Normal']))
    
    # Total
    elements.append(Spacer(1, 12))
    total = sum(item['price'] for item in bill.items)
    elements.append(Paragraph(f"Total: ${total:.2f}", styles['Heading2']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def reset_bill():
    st.session_state.bill = Bill(description="New Bill")
    st.rerun()

# --- Main App Logic ---

st.markdown('<h1 class="main-title">💰 Bill Splitter</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Split bills fairly among friends with ease</p>', unsafe_allow_html=True)

# Initialize state
if 'bill' not in st.session_state:
    st.session_state.bill = Bill(description="New Bill")
if 'all_participants' not in st.session_state:
    st.session_state.all_participants = load_participants()
    for name in st.session_state.all_participants:
        st.session_state.bill.add_participant(name)
if 'groups' not in st.session_state:
    st.session_state.groups = load_groups()

# Top Bar: New Bill Button
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    bill_title = st.text_input("Bill Title", value=st.session_state.bill.description, key="bill_title_input")
    st.session_state.bill.description = bill_title
with col_header_2:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.button("✨ New Bill"):
        reset_bill()

tab1, tab2 = st.tabs(["📝 Bill Entry", "👥 Manage Participants & Groups"])

with tab1:
    # --- Input Section ---
    st.markdown("### ➕ Add Items")
    
    # Group Selection Logic
    if 'group_selector_key' not in st.session_state:
        st.session_state.group_selector_key = 0
    
    def on_group_select():
        group = st.session_state[f"group_select_{st.session_state.group_selector_key}"]
        if group and group != "— Select a group to pre-fill —":
            st.session_state.participant_multiselect = st.session_state.groups[group]
    
    group_options = ["— Select a group to pre-fill —"] + list(st.session_state.groups.keys())
    
    col_input_1, col_input_2 = st.columns([1, 2])
    
    with col_input_1:
         st.selectbox(
            "Quick Select a Group", 
            options=group_options, 
            key=f"group_select_{st.session_state.group_selector_key}",
            on_change=on_group_select
        )
    
    # Callback for adding item
    def add_item_callback():
        name = st.session_state.new_item_name
        price = st.session_state.new_item_price
        participants = st.session_state.participant_multiselect
        
        if name and price > 0 and participants:
            st.session_state.bill.add_item(name, price, participants)
            st.session_state.form_msg = f"✅ Added item: {name}"
            st.session_state.form_msg_type = "success"
            
            # Clear inputs manually since we aren't using clear_on_submit
            st.session_state.new_item_name = ""
            st.session_state.new_item_price = 0.0
            st.session_state.participant_multiselect = []
            st.session_state.group_selector_key += 1 # Reset group selector
        else:
            st.session_state.form_msg = "Please fill all fields and select at least one participant."
            st.session_state.form_msg_type = "error"

    # Display message if exists
    if 'form_msg' in st.session_state and st.session_state.form_msg:
        if st.session_state.form_msg_type == "success":
            st.success(st.session_state.form_msg)
        else:
            st.error(st.session_state.form_msg)
        # Clear message after display so it doesn't persist forever
        st.session_state.form_msg = None

    # Form
    with st.form("add_item_form", clear_on_submit=False):
        c1, c2 = st.columns([1, 1])
        with c1:
            st.text_input("Item Name", placeholder="e.g., Pizza, Drinks", key="new_item_name")
        with c2:
            st.number_input("Item Price", min_value=0.0, format="%.2f", key="new_item_price")
        
        # Participants Multiselect
        if 'participant_multiselect' not in st.session_state:
            st.session_state.participant_multiselect = []

        st.multiselect(
            "Select Participants for this item",
            st.session_state.all_participants,
            key="participant_multiselect"
        )
        
        st.form_submit_button("➕ Add Item", on_click=add_item_callback)
    
    # --- Remove Items ---
    if st.session_state.bill.items:
        with st.expander("🗑️ Remove an Item"):
            item_names = [item['item_name'] for item in st.session_state.bill.items]
            item_to_remove = st.selectbox("Select item to remove", options=item_names)
            if st.button("🗑️ Remove Selected Item"):
                st.session_state.bill.remove_item(item_to_remove)
                st.success(f"✅ Removed item: {item_to_remove}")
                st.rerun()

    # --- Table Section (Full Width) ---
    st.markdown("---")
    st.markdown(f"### 📊 {st.session_state.bill.description}")
    
    if st.session_state.bill.items:
        summary_df = create_bill_dataframe(st.session_state.bill)
        
        # Column Visibility
        participant_cols = [c for c in summary_df.columns if c != 'Total Price']
        
        cols_to_show = st.multiselect("👁️ Show/Hide Columns", participant_cols, default=participant_cols)
        
        if not summary_df.empty:
            # Filter columns: Total Price + Selected Participants
            final_cols = ['Total Price'] + cols_to_show
            df_to_show = summary_df[final_cols]
            
            st.dataframe(
                df_to_show.style.set_properties(**{
                    'font-size': '16px', 
                    'color': 'black'
                }), 
                use_container_width=True
            )
            
            # Totals
            if 'Total Price' in summary_df.columns:
                total_bill = summary_df.loc['Total', 'Total Price']
                st.metric("💵 Total Bill", f"${total_bill:,.2f}")
            
            # Downloads
            st.markdown("#### 💾 Download Options")
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                json_string = get_bill_as_json_string(st.session_state.bill)
                st.download_button(
                    label="📥 Download Bill as JSON",
                    data=json_string,
                    file_name=f"{st.session_state.bill.description.replace(' ', '_')}.json",
                    mime="application/json",
                )
            with c_d2:
                pdf_data = generate_pdf(st.session_state.bill)
                st.download_button(
                    label="📄 Download Bill as PDF",
                    data=pdf_data,
                    file_name=f"{st.session_state.bill.description.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
    else:
        st.info("📋 No items added to the bill yet. Add items to see the breakdown here.")

with tab2:
    st.markdown("### ⚙️ Manage Your Team")
    
    col_p, col_g = st.columns(2)
    with col_p:
        st.markdown("#### 👤 Add or Remove Participants")
        new_p = st.text_input("Add New Participant", key="new_p_input", placeholder="Enter name")
        if st.button("Add Participant"):
            if new_p and new_p not in st.session_state.all_participants:
                st.session_state.all_participants.append(new_p)
                st.session_state.bill.add_participant(new_p)
                save_participants(st.session_state.all_participants)
                st.success(f"✅ Added {new_p}")
                st.rerun()
        
        if st.session_state.all_participants:
            st.markdown("#### Remove Participants")
            rem_p = st.multiselect("Select participants to remove", st.session_state.all_participants)
            if st.button("🗑️ Remove Selected"):
                for p in rem_p:
                    if p in st.session_state.all_participants:
                        st.session_state.all_participants.remove(p)
                save_participants(st.session_state.all_participants)
                st.rerun()

    with col_g:
        st.markdown("#### 👥 Create Groups")
        g_name = st.text_input("New Group Name", placeholder="e.g., Family")
        g_mems = st.multiselect("Select members", st.session_state.all_participants)
        if st.button("✨ Create Group"):
            if g_name and g_mems:
                st.session_state.groups[g_name] = g_mems
                save_groups(st.session_state.groups)
                st.success(f"✅ Group '{g_name}' created.")
                st.rerun()
        
        if st.session_state.groups:
            st.markdown("#### 🗑️ Delete Groups")
            del_g = st.selectbox("Select group to delete", list(st.session_state.groups.keys()))
            if st.button("Delete Group"):
                del st.session_state.groups[del_g]
                save_groups(st.session_state.groups)
                st.rerun()

    # Summary
    st.markdown("---")
    st.markdown(f"**Current Participants:** {', '.join(st.session_state.all_participants)}")