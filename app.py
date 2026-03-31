import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, date
import uuid
import altair as alt

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BrewPoint TPS",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Cream background */
.stApp {
    background-color: #f5efe6;
    color: #3b1f0a;
}

/* Header brand bar */
.brand-header {
    background: linear-gradient(135deg, #4a2410 0%, #7b4020 50%, #4a2410 100%);
    border-bottom: 3px solid #c8853a;
    padding: 18px 32px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #fdf3e3;
    letter-spacing: 0.02em;
    margin: 0;
}
.brand-sub {
    font-size: 0.78rem;
    color: #e8c99a;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #ecdcc8;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #c8a87a;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b3a1f;
    border-radius: 6px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 8px 24px;
}
.stTabs [aria-selected="true"] {
    background: #6b3a1f !important;
    color: #fdf3e3 !important;
}

/* Cards */
.card {
    background: #fdf3e3;
    border: 1px solid #d4aa80;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(107, 58, 31, 0.08);
}
.card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: #4a2410;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #c8853a;
}

/* Metric boxes */
.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
}
.metric-box {
    flex: 1;
    background: #fdf3e3;
    border: 1px solid #c8853a;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(107, 58, 31, 0.10);
}
.metric-val {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: #4a2410;
}
.metric-label {
    font-size: 0.72rem;
    color: #8b5e3c;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

/* Inputs */
div[data-testid="stSelectbox"] > div,
div[data-testid="stNumberInput"] > div > div,
div[data-testid="stTextInput"] > div > div {
    background: #fff8f0 !important;
    border: 1px solid #c8a87a !important;
    color: #3b1f0a !important;
    border-radius: 8px !important;
}

/* Submit button */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6b3a1f, #9b5a30) !important;
    color: #fdf3e3 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 36px !important;
    width: 100% !important;
    letter-spacing: 0.05em;
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(107, 58, 31, 0.30) !important;
}

/* Success / error */
div[data-testid="stAlert"] {
    border-radius: 8px;
}

/* Table */
.stDataFrame {
    border: 1px solid #d4aa80 !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* Label color */
label, .stSelectbox label, .stNumberInput label, .stTextInput label {
    color: #6b3a1f !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* Subheaders */
h2, h3 {
    color: #4a2410 !important;
}

/* Receipt preview */
.receipt {
    background: #fff8f0;
    color: #3b1f0a;
    border-radius: 10px;
    padding: 20px 24px;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.8;
    border-top: 6px dashed #c8853a;
    border: 1px solid #d4aa80;
    box-shadow: 0 2px 8px rgba(107, 58, 31, 0.08);
}
.receipt h4 {
    text-align: center;
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    margin-bottom: 4px;
    color: #4a2410;
}
.receipt hr { border: 1px dashed #c8853a; }
.receipt .total { font-weight: bold; font-size: 1rem; color: #4a2410; }
</style>
""", unsafe_allow_html=True)

# ─── BRAND HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <div>
        <p class="brand-title">☕ BrewPoint Tech Café</p>
        <p class="brand-sub">Transactional Processing System &nbsp;·&nbsp; Georgetown, Guyana</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── PRODUCT CATALOGUE ────────────────────────────────────────────────────────
PRODUCTS = {
    # Beverages
    "Espresso (Single)":         {"code": "BEV-001", "price": 500,  "category": "Beverage"},
    "Espresso (Double)":         {"code": "BEV-002", "price": 700,  "category": "Beverage"},
    "Cappuccino":                {"code": "BEV-003", "price": 900,  "category": "Beverage"},
    "Latte":                     {"code": "BEV-004", "price": 950,  "category": "Beverage"},
    "Cold Brew":                 {"code": "BEV-005", "price": 1100, "category": "Beverage"},
    "Matcha Latte":              {"code": "BEV-006", "price": 1200, "category": "Beverage"},
    # Food
    "Butter Croissant":          {"code": "FOD-001", "price": 600,  "category": "Food"},
    "Avocado Toast":             {"code": "FOD-002", "price": 1500, "category": "Food"},
    "Banana Bread Slice":        {"code": "FOD-003", "price": 500,  "category": "Food"},
    # Tech Accessories
    "USB-C Cable (1m)":          {"code": "TCH-001", "price": 2500, "category": "Tech Accessory"},
    "Screen Protector (Universal)": {"code": "TCH-002", "price": 1800, "category": "Tech Accessory"},
    "Wireless Earbuds (Basic)":  {"code": "TCH-003", "price": 8500, "category": "Tech Accessory"},
    "Phone Stand":               {"code": "TCH-004", "price": 1200, "category": "Tech Accessory"},
    "Power Bank (5000mAh)":      {"code": "TCH-005", "price": 12000,"category": "Tech Accessory"},
}

PAYMENT_METHODS = ["Cash", "Card (Debit/Credit)", "Online Transfer (GTransfer)"]
CUSTOMER_TYPES  = ["Walk-in", "Pre-order (WhatsApp)", "Corporate / Bulk"]
STAFF_LIST      = ["Alicia Chen", "Marcus Ford", "Priya Nair", "Devon Baptiste", "Other"]

# ─── GOOGLE SHEETS CONNECTION ─────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_sheet():
    """Authenticate and return the Google Sheet worksheet."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet  = client.open(st.secrets["sheet_name"]).sheet1
    return sheet

def ensure_headers(sheet):
    """Write column headers if the sheet is empty."""
    headers = [
        "transaction_id", "timestamp", "staff_id", "staff_name",
        "item_code", "item_name", "category",
        "quantity", "unit_price", "total_price",
        "payment_method", "customer_type", "discount_applied", "notes"
    ]
    if sheet.row_count == 0 or sheet.cell(1, 1).value != "transaction_id":
        sheet.insert_row(headers, 1)

def append_transaction(sheet, row: list):
    sheet.append_row(row, value_input_option="USER_ENTERED")

@st.cache_data(ttl=60)
def load_all_transactions(_sheet):
    """Load all rows (excluding header) as a DataFrame."""
    records = _sheet.get_all_records()
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🧾  New Transaction", "📊  Daily Productivity Report"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TRANSACTION ENTRY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_form, col_receipt = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="card"><p class="card-title">🛒 Sale Details</p>', unsafe_allow_html=True)

        item_name    = st.selectbox("Select Item", list(PRODUCTS.keys()))
        item_info    = PRODUCTS[item_name]
        unit_price   = item_info["price"]

        c1, c2 = st.columns(2)
        with c1:
            quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1, step=1)
        with c2:
            discount = st.number_input("Discount (GYD)", min_value=0, max_value=10000, value=0, step=100)

        total_price = max(0, (unit_price * quantity) - discount)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><p class="card-title">👤 Transaction Info</p>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            staff_name = st.selectbox("Staff Member", STAFF_LIST)
            if staff_name == "Other":
                staff_name = st.text_input("Enter Staff Name")
        with c4:
            customer_type = st.selectbox("Customer Type", CUSTOMER_TYPES)

        payment_method = st.selectbox("Payment Method", PAYMENT_METHODS)
        notes          = st.text_input("Notes (optional)", placeholder="e.g. extra shot, bulk order")

        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.button("✅  Record Transaction")

    # ── RECEIPT PREVIEW ──────────────────────────────────────────────────────
    with col_receipt:
        now_str = datetime.now().strftime("%d %b %Y  %H:%M")
        st.markdown(f"""
        <div class="receipt">
            <h4>☕ BrewPoint Tech Café</h4>
            <p style="text-align:center;font-size:0.75rem;color:#666;">{now_str}</p>
            <hr/>
            <p><b>Item:</b> {item_name}</p>
            <p><b>Code:</b> {item_info['code']}</p>
            <p><b>Category:</b> {item_info['category']}</p>
            <p><b>Unit Price:</b> GYD {unit_price:,}</p>
            <p><b>Qty:</b> {quantity}</p>
            <p><b>Discount:</b> GYD {discount:,}</p>
            <hr/>
            <p class="total">TOTAL: GYD {total_price:,}</p>
            <hr/>
            <p><b>Staff:</b> {staff_name}</p>
            <p><b>Payment:</b> {payment_method}</p>
            <p><b>Customer:</b> {customer_type}</p>
            {"<p><b>Notes:</b> " + notes + "</p>" if notes else ""}
        </div>
        """, unsafe_allow_html=True)

    # ── SUBMIT LOGIC ─────────────────────────────────────────────────────────
    if submitted:
        if not staff_name or staff_name.strip() == "":
            st.error("⚠️ Please enter a staff name before submitting.")
        else:
            try:
                sheet = get_sheet()
                ensure_headers(sheet)

                txn_id    = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"
                staff_id  = f"STF-{staff_name[:3].upper()}"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                row = [
                    txn_id, timestamp, staff_id, staff_name,
                    item_info["code"], item_name, item_info["category"],
                    quantity, unit_price, total_price,
                    payment_method, customer_type, discount, notes
                ]
                append_transaction(sheet, row)
                load_all_transactions.clear()

                st.success(f"✅ Transaction **{txn_id}** recorded — GYD {total_price:,}")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Could not save transaction: {e}")
                st.info("💡 Make sure your Google Sheets credentials are set in `.streamlit/secrets.toml`")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DAILY PRODUCTIVITY REPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="card"><p class="card-title">📅 Daily Productivity Report</p>', unsafe_allow_html=True)

    try:
        sheet = get_sheet()
        df    = load_all_transactions(sheet)

        if df.empty:
            st.info("No transactions recorded yet. Start selling to see your report!")
        else:
            df["timestamp"]   = pd.to_datetime(df["timestamp"])
            df["total_price"] = pd.to_numeric(df["total_price"], errors="coerce").fillna(0)
            df["quantity"]    = pd.to_numeric(df["quantity"],    errors="coerce").fillna(0)
            df["unit_price"]  = pd.to_numeric(df["unit_price"],  errors="coerce").fillna(0)

            # ── Date filter ──────────────────────────────────────────────────
            col_date, _ = st.columns([2, 4])
            with col_date:
                selected_date = st.date_input("Filter by Date", value=date.today())

            df_day = df[df["timestamp"].dt.date == selected_date]

            if df_day.empty:
                st.warning(f"No transactions found for {selected_date.strftime('%d %b %Y')}.")
            else:
                # ── KPI Metrics ───────────────────────────────────────────────
                total_revenue  = df_day["total_price"].sum()
                total_txns     = len(df_day)
                units_sold     = int(df_day["quantity"].sum())
                avg_txn        = total_revenue / total_txns if total_txns else 0

                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-box">
                        <div class="metric-val">GYD {total_revenue:,.0f}</div>
                        <div class="metric-label">Total Revenue</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-val">{total_txns}</div>
                        <div class="metric-label">Transactions</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-val">{units_sold}</div>
                        <div class="metric-label">Units Sold</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-val">GYD {avg_txn:,.0f}</div>
                        <div class="metric-label">Avg Transaction</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Bar Chart ─────────────────────────────────────────────────
                st.subheader("Units Sold by Item")
                item_summary = (
                    df_day.groupby("item_name")["quantity"]
                    .sum()
                    .reset_index()
                    .sort_values("quantity", ascending=False)
                )

                chart = (
                    alt.Chart(item_summary)
                    .mark_bar(color="#7b4020", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("item_name:N", sort="-y", title="Item", axis=alt.Axis(labelAngle=-30)),
                        y=alt.Y("quantity:Q", title="Units Sold"),
                        tooltip=["item_name", "quantity"],
                    )
                    .properties(height=300)
                    .configure_view(strokeWidth=0, fill="#fdf3e3")
                    .configure_axis(
                        gridColor="#ecdcc8",
                        domainColor="#d4aa80",
                        labelColor="#6b3a1f",
                        titleColor="#4a2410",
                    )
                )
                st.altair_chart(chart, use_container_width=True)

                # ── Revenue by Category ───────────────────────────────────────
                st.subheader("Revenue by Category")
                cat_summary = (
                    df_day.groupby("category")["total_price"]
                    .sum()
                    .reset_index()
                    .sort_values("total_price", ascending=False)
                )
                cat_chart = (
                    alt.Chart(cat_summary)
                    .mark_bar(color="#c8853a", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("category:N", title="Category"),
                        y=alt.Y("total_price:Q", title="Revenue (GYD)"),
                        tooltip=["category", "total_price"],
                    )
                    .properties(height=250)
                    .configure_view(strokeWidth=0, fill="#fdf3e3")
                    .configure_axis(
                        gridColor="#ecdcc8",
                        domainColor="#d4aa80",
                        labelColor="#6b3a1f",
                        titleColor="#4a2410",
                    )
                )
                st.altair_chart(cat_chart, use_container_width=True)

                # ── Full Transaction Table ────────────────────────────────────
                st.subheader("Transaction Log")
                display_cols = [
                    "transaction_id", "timestamp", "staff_name",
                    "item_name", "category", "quantity",
                    "unit_price", "total_price", "payment_method", "customer_type"
                ]
                st.dataframe(
                    df_day[display_cols].sort_values("timestamp", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                )

                # ── Staff Performance ─────────────────────────────────────────
                st.subheader("Staff Performance")
                staff_perf = (
                    df_day.groupby("staff_name")
                    .agg(transactions=("transaction_id", "count"),
                         revenue=("total_price", "sum"))
                    .reset_index()
                    .sort_values("revenue", ascending=False)
                )
                st.dataframe(staff_perf, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Could not load data: {e}")
        st.info("💡 Check your Google Sheets API credentials in `.streamlit/secrets.toml`")

    st.markdown('</div>', unsafe_allow_html=True)
