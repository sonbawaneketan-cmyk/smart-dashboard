import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import base64
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Smart Data Dashboard", layout="wide")

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

/* MAIN BACKGROUND */
.main {
    background-color: #0f172a;
    color: white;
}

/* SIDEBAR FIX */
section[data-testid="stSidebar"] {
    background-color: #f1f5f9;
}
section[data-testid="stSidebar"] * {
    color: black !important;
}

/* CARD STYLE */
.card {
    background: #1e293b;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    color: white;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

st.title("📊 Smart Data Cleaning & Visualization Dashboard")

# =========================
# SESSION STATE
# =========================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Name", "Category", "Amount"])

# =========================
# FUNCTIONS
# =========================
def clean_data(df):
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df.dropna(inplace=True)
    df["Name"] = df["Name"].astype(str).str.title()
    df["Category"] = df["Category"].astype(str).str.title()
    return df

def parse_text(text):
    pattern = r"(\w+)\s+(\w+)\s+(\d+)"
    matches = re.findall(pattern, text.lower())
    return pd.DataFrame(matches, columns=["Name", "Category", "Amount"])

# ✅ HTML REPORT (MATPLOTLIB IMAGES)
def create_html_report(df, total, top_category):
    if df.empty:
        return "<h1>No Data Available</h1>"

    chart_data = df.groupby("Category")["Amount"].sum()

    # BAR CHART
    fig1, ax1 = plt.subplots(figsize=(4,3))
    chart_data.plot(kind="bar", ax=ax1)
    ax1.set_title("Category vs Amount")

    buf1 = BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    bar_img = base64.b64encode(buf1.read()).decode("utf-8")
    plt.close(fig1)

    # PIE CHART
    fig2, ax2 = plt.subplots(figsize=(4,3))
    chart_data.plot(kind="pie", autopct="%1.1f%%", ax=ax2)
    ax2.set_ylabel("")

    buf2 = BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    pie_img = base64.b64encode(buf2.read()).decode("utf-8")
    plt.close(fig2)

    # HTML DESIGN
    html = f"""
    <html>
    <head>
        <title>Smart Data Report</title>

        <style>
            body {{
                margin: 0;
                font-family: Arial;
                background: #f5f5f5;
            }}

            .container {{
                max-width: 1100px;
                margin: auto;
                padding: 20px;
            }}

            .cards {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }}

            .card {{
                flex: 1;
                background: #1e293b;
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            }}

            .charts {{
                display: flex;
                gap: 20px;
            }}

            .chart-box {{
                flex: 1;
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
                text-align: center;
            }}

            img {{
                width: 100%;
                height: auto;
            }}

            h2 {{
                margin-bottom: 10px;
            }}
        </style>
    </head>

    <body>

        <div class="container">

            <!-- SUMMARY CARDS -->
            <div class="cards">
                <div class="card">
                    <h2>Total Amount</h2>
                    <h1>₹ {total}</h1>
                </div>

                <div class="card">
                    <h2>Top Category</h2>
                    <h1>{top_category}</h1>
                </div>
            </div>

            <!-- CHARTS -->
            <div class="charts">

                <div class="chart-box">
                    <h2>Bar Chart</h2>
                    <img src="data:image/png;base64,{bar_img}">
                </div>

                <div class="chart-box">
                    <h2>Pie Chart</h2>
                    <img src="data:image/png;base64,{pie_img}">
                </div>

            </div>

        </div>

    </body>
    </html>
    """

    return html

# =========================
# INPUT
# =========================
st.sidebar.header("📌 Input Options")

option = st.sidebar.radio(
    "Choose Input Method",
    ["Upload CSV", "Manual Entry", "Raw Text Input"]
)

df = st.session_state.data

if option == "Upload CSV":
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file:
        df = pd.read_csv(file)
        df = clean_data(df)

elif option == "Manual Entry":
    name = st.text_input("Name")
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0)

    if st.button("Add"):
        new = pd.DataFrame([[name, category, amount]],
                           columns=["Name", "Category", "Amount"])
        df = pd.concat([df, new], ignore_index=True)
        df = clean_data(df)

elif option == "Raw Text Input":
    text = st.text_area("Enter text (e.g. ram food 200)")

    if st.button("Convert"):
        df = parse_text(text)
        df = clean_data(df)

st.session_state.data = df

# =========================
# TABLE
# =========================
st.subheader("📋 Dataset")
st.dataframe(df, use_container_width=True, height=200)

# =========================
# FILTER
# =========================
st.sidebar.header("🔎 Filters")

if not df.empty:
    categories = df["Category"].unique()
    selected = st.sidebar.selectbox("Category", ["All"] + list(categories))

    if selected != "All":
        df = df[df["Category"] == selected]

# =========================
# SUMMARY
# =========================
st.subheader("📌 Summary")

total = df["Amount"].sum() if not df.empty else 0
top = df.groupby("Category")["Amount"].sum().idxmax() if not df.empty else "N/A"

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>Total Amount</h3>
        <h2>₹ {total}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>Top Category</h3>
        <h2>{top}</h2>
    </div>
    """, unsafe_allow_html=True)

# =========================
# VISUALIZATION
# =========================
st.subheader("📊 Visualizations")

if not df.empty:
    chart_data = df.groupby("Category")["Amount"].sum()

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(4,3))
        chart_data.plot(kind="bar", ax=ax)
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(4,3))
        chart_data.plot(kind="pie", autopct="%1.1f%%", ax=ax2)
        ax2.set_ylabel("")
        st.pyplot(fig2)

# =========================
# DOWNLOAD
# =========================
st.subheader("📥 Download Report")

html_report = create_html_report(df, total, top)

st.download_button(
    "🌐 Download Report",
    html_report,
    "report.html",
    "text/html"
)