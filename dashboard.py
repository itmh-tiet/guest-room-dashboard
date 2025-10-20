import streamlit as st
import pandas as pd
import gspread
import os, json
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh

# -----------------------------------------------------------
# 🔐 GOOGLE AUTHENTICATION (Local + Streamlit Cloud Hybrid)
# -----------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    if "CREDS_JSON" in os.environ:
        creds_dict = json.loads(os.environ["CREDS_JSON"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        st.sidebar.success("☁️ Using Streamlit Cloud secrets")
    else:
        creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)
        st.sidebar.info("💻 Using local creds.json file")
except Exception as e:
    st.error(f"❌ Failed to load credentials: {e}")
    st.stop()

# -----------------------------------------------------------
# 🧾 GOOGLE SHEET CONFIGURATION
# -----------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Hg7B61fUjouI_-R0bSm2aFxqM_gI89QlXZoNAFJYi1w"
SHEET_NAME = "Guest Room Dashboard"

try:
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SPREADSHEET_URL).worksheet(SHEET_NAME)
    data = pd.DataFrame(sheet.get_all_records())
except Exception as e:
    st.error("❌ Failed to load Google Sheet. Please check your credentials or sheet access.")
    st.exception(e)
    st.stop()

# -----------------------------------------------------------
# 🧹 DATA PREPARATION
# -----------------------------------------------------------
if data.empty:
    st.warning("⚠️ The sheet is empty or not formatted correctly.")
    st.stop()

data.columns = [c.strip().title() for c in data.columns]

# Detect bookings
data["Booked"] = data.apply(
    lambda r: any("BOOKED" in str(v).upper() for v in r.values), axis=1
)

total_rooms = len(data)
booked_rooms = data["Booked"].sum()
available_rooms = total_rooms - booked_rooms

# -----------------------------------------------------------
# 🖥️ STREAMLIT PAGE LAYOUT
# -----------------------------------------------------------
st.set_page_config(page_title="Thapar Guest Room Dashboard", page_icon="🏨", layout="wide")
st.title("🏨 Thapar Guest Room Dashboard")

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="data_refresh")

# Summary Cards
c1, c2, c3 = st.columns(3)
c1.metric("Total Rooms", total_rooms)
c2.metric("Booked", booked_rooms)
c3.metric("Available", available_rooms)

# Filter by Hostel
hostels = sorted(data["Hostel"].unique()) if "Hostel" in data.columns else []
selected_hostel = st.selectbox("🏠 Filter by Hostel", ["All"] + hostels)

if selected_hostel != "All":
    df = data[data["Hostel"] == selected_hostel]
else:
    df = data

# Show Data Table
st.dataframe(df, use_container_width=True)

# Bar Chart by Hostel
st.subheader("📊 Bookings per Hostel")
if "Hostel" in data.columns:
    chart = data.groupby("Hostel")["Booked"].sum().reset_index()
    chart["Booked"] = chart["Booked"].astype(int)
    st.bar_chart(chart.set_index("Hostel"))

# Footer
st.caption("Powered by Streamlit • Live synced with Google Sheets")
