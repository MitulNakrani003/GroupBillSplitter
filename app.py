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

# --- Bootstrap CSS/JS and Custom Styling ---
st.markdown("""
<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<!-- Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<!-- Bootstrap Icons -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

<style>
    /* ============================================
       GLOBAL STYLES & TYPOGRAPHY
       ============================================ */
    
    :root {
        --primary-color: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --secondary-color: #0ea5e9;
        --success-color: #10b981;
        --success-dark: #059669;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-color: #1e293b;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
    }
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary);
    }
    
    /* Main container */
    .block-container {
        max-width: 1400px !important;
        padding: 1.5rem 2rem !important;
        background: var(--bg-light);
    }
    
    /* ============================================
       HEADER CARD
       ============================================ */
    
    .header-card {
        background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 50%, #a855f7 100%);
        border-radius: var(--radius-xl);
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    
    .header-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .header-card h1 {
        font-size: 2.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
        letter-spacing: -0.02em;
    }
    
    .header-card p {
        font-size: 1.125rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
        position: relative;
    }
    
    /* ============================================
       BOOTSTRAP CARDS & SECTIONS
       ============================================ */
    
    .bs-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    
    .bs-card:hover {
        box-shadow: var(--shadow-md);
    }
    
    .bs-card-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--primary-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .bs-card-header i {
        color: var(--primary-color);
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.25rem;
        letter-spacing: -0.01em;
    }
    
    .section-header i {
        color: var(--primary-color);
        font-size: 1.375rem;
    }
    
    /* ============================================
       CUSTOM TABLE STYLING
       ============================================ */
    
    .custom-table-wrapper {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        overflow: hidden;
        margin: 1.5rem 0;
    }
    
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Poppins', sans-serif;
    }
    
    .custom-table thead {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
    }
    
    .custom-table thead th {
        padding: 1rem 1.25rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: none;
    }
    
    .custom-table thead th:first-child {
        border-radius: var(--radius-lg) 0 0 0;
    }
    
    .custom-table thead th:last-child {
        border-radius: 0 var(--radius-lg) 0 0;
    }
    
    .custom-table tbody tr {
        transition: background-color 0.15s ease;
        border-bottom: 1px solid var(--border-color);
    }
    
    .custom-table tbody tr:hover {
        background-color: #f1f5f9;
    }
    
    .custom-table tbody tr:last-child {
        border-bottom: none;
    }
    
    .custom-table tbody td {
        padding: 1rem 1.25rem;
        font-size: 0.9375rem;
        color: var(--text-primary);
        font-weight: 400;
    }
    
    .custom-table tbody tr.total-row {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        font-weight: 600;
    }
    
    .custom-table tbody tr.total-row td {
        color: var(--success-dark);
        font-weight: 600;
        font-size: 1rem;
    }
    
    .custom-table .price-cell {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .custom-table .price-cell.highlight {
        color: var(--success-dark);
        font-weight: 600;
    }
    
    .custom-table .zero-cell {
        color: var(--text-muted);
        font-style: italic;
    }
    
    .custom-table .item-name {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* ============================================
       STREAMLIT INPUTS OVERRIDE
       ============================================ */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        font-family: 'Poppins', sans-serif !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.625rem 1rem !important;
        font-size: 0.9375rem !important;
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Labels */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stMultiSelect > label {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.375rem !important;
    }
    
    /* ============================================
       BUTTONS
       ============================================ */
    
    .stButton > button {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 0.625rem 1.25rem !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
        width: 100%;
        letter-spacing: 0.01em;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        background: linear-gradient(135deg, var(--primary-dark) 0%, #4338ca 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Form submit button */
    .stFormSubmitButton > button {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, var(--success-color) 0%, var(--success-dark) 100%) !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        width: 100%;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        background: linear-gradient(135deg, var(--success-dark) 0%, #047857 100%) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, var(--secondary-color) 0%, #0284c7 100%) !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 0.625rem 1.25rem !important;
        font-size: 0.9375rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    }
    
    /* ============================================
       SELECT BOXES & MULTISELECT
       ============================================ */
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        font-family: 'Poppins', sans-serif !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        background-color: var(--bg-card) !important;
        transition: all 0.2s ease !important;
    }
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--primary-light) !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Multiselect tags */
    .stMultiSelect > div > div > div > div {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border-radius: 2rem !important;
        border: none !important;
        font-size: 0.8125rem !important;
        font-weight: 500 !important;
        padding: 0.25rem 0.75rem !important;
    }
    
    /* ============================================
       TABS
       ============================================ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-card);
        padding: 0.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Poppins', sans-serif !important;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: var(--text-secondary);
        background: transparent;
        font-size: 0.9375rem;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-color);
        background: rgba(99, 102, 241, 0.08);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-sm);
    }
    
    /* ============================================
       ALERTS & MESSAGES
       ============================================ */
    
    .stSuccess {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border: 1px solid #86efac !important;
        border-left: 4px solid var(--success-color) !important;
        border-radius: var(--radius-md) !important;
        color: #166534 !important;
        font-weight: 500 !important;
    }
    
    .stError {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%) !important;
        border: 1px solid #fca5a5 !important;
        border-left: 4px solid var(--danger-color) !important;
        border-radius: var(--radius-md) !important;
        color: #991b1b !important;
        font-weight: 500 !important;
    }
    
    .stWarning {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%) !important;
        border: 1px solid #fcd34d !important;
        border-left: 4px solid var(--warning-color) !important;
        border-radius: var(--radius-md) !important;
        color: #92400e !important;
        font-weight: 500 !important;
    }
    
    .stInfo {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
        border: 1px solid #7dd3fc !important;
        border-left: 4px solid var(--secondary-color) !important;
        border-radius: var(--radius-md) !important;
        color: #075985 !important;
        font-weight: 500 !important;
    }
    
    .alert-custom {
        font-family: 'Poppins', sans-serif;
        padding: 1rem 1.25rem;
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .alert-info-custom {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #7dd3fc;
        border-left: 4px solid var(--secondary-color);
        color: #075985;
        font-weight: 500;
    }
    
    /* ============================================
       FORM CONTAINER
       ============================================ */
    
    [data-testid="stForm"] {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* ============================================
       EXPANDER (ACCORDION)
       ============================================ */
    
    .stExpander {
        background: var(--bg-card);
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
        overflow: hidden;
    }
    
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        border-bottom: 1px solid #fca5a5;
    }
    
    .stExpander > div:first-child p {
        font-family: 'Poppins', sans-serif !important;
        color: #991b1b !important;
        font-weight: 600 !important;
    }
    
    /* ============================================
       METRICS
       ============================================ */
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, var(--success-color) 0%, var(--success-dark) 100%);
        border: none;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Poppins', sans-serif !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: white !important;
        font-size: 2.25rem !important;
        font-weight: 700 !important;
    }
    
    /* ============================================
       DATAFRAME OVERRIDE (fallback)
       ============================================ */
    
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }
    
    /* ============================================
       PARTICIPANT BADGES
       ============================================ */
    
    .participant-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.75rem;
    }
    
    .participant-badge {
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.875rem;
        font-weight: 500;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .participant-badge:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* ============================================
       DIVIDER
       ============================================ */
    
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* ============================================
       TOTAL CARD
       ============================================ */
    
    .total-card {
        background: linear-gradient(135deg, var(--success-color) 0%, var(--success-dark) 100%);
        border-radius: var(--radius-lg);
        padding: 1.5rem 2rem;
        color: white;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0;
    }
    
    .total-card .total-label {
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .total-card .total-amount {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* ============================================
       GROUP CARD
       ============================================ */
    
    .group-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 0.375rem 0.875rem;
        border-radius: 2rem;
        font-size: 0.8125rem;
        font-weight: 600;
        margin: 0.25rem;
        border: 1px solid #fcd34d;
    }
</style>

<!-- Bootstrap JS Bundle -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def generate_custom_table_html(df):
    """Generate a custom Bootstrap-styled HTML table from DataFrame."""
    html = '<div class="custom-table-wrapper"><table class="custom-table">'
    
    # Header
    html += '<thead><tr>'
    html += '<th>Item</th>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead>'
    
    # Body
    html += '<tbody>'
    for idx, row in df.iterrows():
        row_class = 'total-row' if idx == 'Total' else ''
        html += f'<tr class="{row_class}">'
        
        # Item name column
        if idx == 'Total':
            html += f'<td class="item-name" style="font-weight: 700;">Total</td>'
        else:
            html += f'<td class="item-name">{idx}</td>'
        
        # Data columns
        for col in df.columns:
            val = row[col]
            if val == 0:
                html += '<td class="zero-cell">-</td>'
            elif col == 'Total Price':
                cell_class = 'price-cell highlight' if idx == 'Total' else 'price-cell'
                html += f'<td class="{cell_class}">${val:,.2f}</td>'
            else:
                cell_class = 'price-cell highlight' if idx == 'Total' else 'price-cell'
                html += f'<td class="{cell_class}">${val:.2f}</td>'
        
        html += '</tr>'
    html += '</tbody></table></div>'
    
    return html

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

# Bootstrap Header Card
st.markdown('''
<div class="header-card">
    <h1><i class="bi bi-receipt-cutoff me-3"></i>Bill Splitter</h1>
    <p>Split expenses fairly and effortlessly with your friends</p>
</div>
''', unsafe_allow_html=True)

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
    bill_title = st.text_input("Bill Title", value=st.session_state.bill.description, key="bill_title_input", label_visibility="collapsed", placeholder="Enter bill title...")
    st.session_state.bill.description = bill_title
with col_header_2:
    if st.button("New Bill", key="new_bill_btn"):
        reset_bill()

tab1, tab2 = st.tabs(["📝 Bill Entry", "👥 Participants & Groups"])

with tab1:
    # --- Input Section ---
    st.markdown('<div class="section-header"><i class="bi bi-plus-circle"></i> Add Items</div>', unsafe_allow_html=True)
    
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
            st.session_state.form_msg = f"Added item: {name}"
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
        
        st.form_submit_button("Add Item", on_click=add_item_callback)
    
    # --- Remove Items ---
    if st.session_state.bill.items:
        with st.expander("🗑️ Remove an Item", expanded=False):
            item_names = [item['item_name'] for item in st.session_state.bill.items]
            item_to_remove = st.selectbox("Select item to remove", options=item_names)
            if st.button("Remove Selected Item", key="remove_item_btn"):
                st.session_state.bill.remove_item(item_to_remove)
                st.success(f"Removed item: {item_to_remove}")
                st.rerun()

    # --- Table Section (Full Width) ---
    st.markdown("---")
    st.markdown(f'''
    <div class="section-header">
        <i class="bi bi-table"></i> {st.session_state.bill.description}
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.bill.items:
        summary_df = create_bill_dataframe(st.session_state.bill)
        
        # Column Visibility
        participant_cols = [c for c in summary_df.columns if c != 'Total Price']
        
        cols_to_show = st.multiselect("Show/Hide Participants", participant_cols, default=participant_cols, key="column_visibility")
        
        if not summary_df.empty:
            # Filter columns: Total Price + Selected Participants
            final_cols = ['Total Price'] + cols_to_show
            df_to_show = summary_df[final_cols].round(2)
            
            # Render custom HTML table
            table_html = generate_custom_table_html(df_to_show)
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Totals with custom card
            if 'Total Price' in summary_df.columns:
                total_bill = summary_df.loc['Total', 'Total Price']
                st.markdown(f'''
                <div class="total-card">
                    <div class="total-label">
                        <i class="bi bi-cash-stack me-2"></i>Total Bill Amount
                    </div>
                    <div class="total-amount">${total_bill:,.2f}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Downloads
            st.markdown('<div class="section-header"><i class="bi bi-download"></i> Download Options</div>', unsafe_allow_html=True)
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                json_string = get_bill_as_json_string(st.session_state.bill)
                st.download_button(
                    label="Download JSON",
                    data=json_string,
                    file_name=f"{st.session_state.bill.description.replace(' ', '_')}.json",
                    mime="application/json",
                )
            with c_d2:
                pdf_data = generate_pdf(st.session_state.bill)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=f"{st.session_state.bill.description.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
    else:
        st.markdown('''
        <div class="alert-custom alert-info-custom">
            <i class="bi bi-info-circle me-2"></i>
            No items added to the bill yet. Add items above to see the breakdown here.
        </div>
        ''', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header"><i class="bi bi-gear"></i> Manage Your Team</div>', unsafe_allow_html=True)
    
    col_p, col_g = st.columns(2)
    with col_p:
        st.markdown('''
        <div class="bs-card">
            <div class="bs-card-header"><i class="bi bi-person-plus me-2"></i>Participants</div>
        </div>
        ''', unsafe_allow_html=True)
        new_p = st.text_input("Add New Participant", key="new_p_input", placeholder="Enter name")
        if st.button("Add Participant", key="add_participant_btn"):
            if new_p and new_p not in st.session_state.all_participants:
                st.session_state.all_participants.append(new_p)
                st.session_state.bill.add_participant(new_p)
                save_participants(st.session_state.all_participants)
                st.success(f"Added {new_p}")
                st.rerun()
        
        if st.session_state.all_participants:
            st.markdown("##### Remove Participants")
            rem_p = st.multiselect("Select participants to remove", st.session_state.all_participants)
            if st.button("Remove Selected", key="remove_participants_btn"):
                for p in rem_p:
                    if p in st.session_state.all_participants:
                        st.session_state.all_participants.remove(p)
                save_participants(st.session_state.all_participants)
                st.rerun()

    with col_g:
        st.markdown('''
        <div class="bs-card">
            <div class="bs-card-header"><i class="bi bi-people me-2"></i>Groups</div>
        </div>
        ''', unsafe_allow_html=True)
        g_name = st.text_input("New Group Name", placeholder="e.g., Family")
        g_mems = st.multiselect("Select members", st.session_state.all_participants, key="group_members")
        if st.button("Create Group", key="create_group_btn"):
            if g_name and g_mems:
                st.session_state.groups[g_name] = g_mems
                save_groups(st.session_state.groups)
                st.success(f"Group '{g_name}' created.")
                st.rerun()
        
        if st.session_state.groups:
            st.markdown("##### Delete Groups")
            del_g = st.selectbox("Select group to delete", list(st.session_state.groups.keys()))
            if st.button("Delete Group", key="delete_group_btn"):
                del st.session_state.groups[del_g]
                save_groups(st.session_state.groups)
                st.rerun()

    # Summary with Bootstrap badges
    st.markdown("---")
    if st.session_state.all_participants:
        participant_badges = ' '.join([f'<span class="participant-badge">{p}</span>' for p in st.session_state.all_participants])
        st.markdown(f'''
        <div class="bs-card">
            <strong>Current Participants:</strong>
            <div class="participant-list">
                {participant_badges}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="alert-custom alert-info-custom">
            <i class="bi bi-info-circle me-2"></i>
            No participants added yet. Add participants above to get started.
        </div>
        ''', unsafe_allow_html=True)