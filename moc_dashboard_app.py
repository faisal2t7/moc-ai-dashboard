import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
from datetime import datetime

st.set_page_config(page_title="Military MOC AI Dashboard", layout="centered")
st.info("✅ App has started running...")

# Load secrets
load_dotenv()
EMAIL = os.getenv("EMAIL_USER")
PASS = os.getenv("EMAIL_PASS")

# === Utility Functions ===
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("ai_memory.csv")
        return df
    except:
        return pd.DataFrame(columns=["Staff Name", "MOC Description", "Hours Spent", "MOC Count", "Month", "Level"])

def save_data(df):
    df.to_csv("ai_memory.csv", index=False)

def auto_assign_level(row):
    if row["MOC Count"] >= 5 and row["Hours Spent"] >= 20:
        return 7
    elif row["MOC Count"] >= 3 and row["Hours Spent"] >= 10:
        return 5
    else:
        return 3

# === Page Layout ===
st.title("📊 Military MOC AI Dashboard")

# === Login ===
with st.sidebar:
    st.header("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if user != "admin" or pwd != "mocpass":
        st.warning("Invalid credentials.")
        st.stop()

# === Load & Display Data ===
df = load_data()
if df.empty:
    st.warning("No data found.")
else:
    df["Level"] = df.apply(auto_assign_level, axis=1)

# === Upload New Data ===
st.sidebar.subheader("➕ Add MOC Entry")
with st.sidebar.form("entry_form", clear_on_submit=True):
    name = st.text_input("Staff Name")
    desc = st.text_input("MOC Description")
    hours = st.number_input("Hours Spent", min_value=0, value=1)
    count = st.number_input("MOC Count", min_value=1, value=1)
    month = datetime.now().strftime("%B")
    submitted = st.form_submit_button("Add Entry")

if submitted and name and desc:
    new_entry = {
        "Staff Name": name,
        "MOC Description": desc,
        "Hours Spent": hours,
        "MOC Count": count,
        "Month": month,
        "Level": 0  # Will be auto-assigned
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df["Level"] = df.apply(auto_assign_level, axis=1)
    save_data(df)
    st.success("✅ Entry added and AI memory updated.")

# === Filters ===
with st.sidebar:
    st.subheader("🔎 Filters")
    staff = st.multiselect("Filter by Staff", df["Staff Name"].unique())
    levels = st.multiselect("Filter by Level", df["Level"].unique())
    months = st.multiselect("Filter by Month", df["Month"].unique())

filtered_df = df.copy()
if staff:
    filtered_df = filtered_df[filtered_df["Staff Name"].isin(staff)]
if levels:
    filtered_df = filtered_df[filtered_df["Level"].isin(levels)]
if months:
    filtered_df = filtered_df[filtered_df["Month"].isin(months)]

st.dataframe(filtered_df, use_container_width=True)

# === Summary Metrics ===
st.subheader("📈 Summary")
summary = filtered_df.groupby(["Staff Name", "Level"]).agg({
    "MOC Count": "sum",
    "Hours Spent": "sum"
}).reset_index()

col1, col2, col3 = st.columns(3)
col1.metric("Total MOCs", int(filtered_df["MOC Count"].sum()))
col2.metric("Total Hours", int(filtered_df["Hours Spent"].sum()))
col3.metric("Unique Staff", filtered_df["Staff Name"].nunique())

# === Charts ===
st.subheader("📊 Visualizations")
col_a, col_b = st.columns(2)

with col_a:
    fig1, ax1 = plt.subplots()
    filtered_df.groupby("Staff Name")["Hours Spent"].sum().plot(kind="barh", ax=ax1)
    ax1.set_title("Hours by Staff")
    st.pyplot(fig1)

with col_b:
    fig2, ax2 = plt.subplots()
    filtered_df["MOC Description"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
    ax2.set_ylabel("")
    ax2.set_title("MOC Distribution")
    st.pyplot(fig2)

# === Promotion Candidates ===
st.subheader("🎖️ Promotion Watch")
promote = summary[(summary["MOC Count"] >= 5) & (summary["Hours Spent"] >= 20) & (summary["Level"] < 7)]
if not promote.empty:
    st.success("These staff are eligible for promotion:")
    st.dataframe(promote)
else:
    st.info("No current promotion candidates.")

# === Email Function ===
def send_email(data):
    body = "Staff eligible for promotion:\n\n"
    for _, row in data.iterrows():
        body += f"- {row['Staff Name']} | Level {row['Level']} | {row['MOC Count']} MOCs | {row['Hours Spent']} Hours\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = "📬 MOC Promotion Candidates"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASS)
            server.sendmail(EMAIL, EMAIL, msg.as_string())
            return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

if not promote.empty and st.button("📤 Send Email Alert"):
    if send_email(promote):
        st.success("Email sent successfully!")

# === PDF Export ===
st.subheader("📄 Download PDF Report")
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="MOC AI Summary Report", ln=True, align="C")
    pdf.ln(10)
    for _, row in data.iterrows():
        line = f"{row['Staff Name']} | Level {row['Level']} | {row['MOC Count']} MOCs | {row['Hours Spent']} hrs"
        pdf.cell(200, 10, txt=line, ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

pdf_bytes = generate_pdf(summary)
st.download_button("⬇ Download PDF", data=pdf_bytes, file_name="summary_report.pdf", mime="application/pdf")