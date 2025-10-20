import streamlit as st
import pandas as pd
import gspread
import os, json, io
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------
# ✅ CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Thapar Guest Room Dashboard", page_icon="🏨", layout="wide")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Hg7B61fUjouI_-R0bSm2aFxqM_gI89QlXZoNAFJYi1w"
SHEET_NAME = "Guest Room Dashboard"

# --------------------------------------------------
# ✅ GOOGLE SHEETS CONNECTION (via Streamlit Secrets)
# --------------------------------------------------
try:
    creds_dict = json.loads(os.environ["CREDS_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SPREADSHEET_URL).worksheet(SHEET_NAME)
    data = pd.DataFrame(sheet.get_all_records())
except Exception as e:
    st.error("❌ Failed to load Google Sheet. Please check your credentials or sheet access.")
    st.stop()

# --------------------------------------------------
# 🧮 DATA PREPARATION
# --------------------------------------------------
if data.empty:
    st.warning("No data found in the sheet.")
    st.stop()

data.columns = [c.strip().title() for c in data.columns]

# Mark if any cell in the row contains "BOOKED"
data["Booked"] = data.apply(
    lambda r: any("BOOKED" in str(v).upper() for v in r.values), axis=1
)

total_rooms = len(data)
booked_rooms = int(data["Booked"].sum())
available_rooms = total_rooms - booked_rooms

# --------------------------------------------------
# 🧭 AUTO REFRESH (every 60 sec)
# --------------------------------------------------
st_autorefresh(interval=60 * 1000, key="data_refresh")

# --------------------------------------------------
# 🖥️ DASHBOARD UI
# --------------------------------------------------
st.title("🏨 Thapar Guest Room Dashboard")

with st.container():
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rooms", total_rooms)
    c2.metric("Booked", booked_rooms)
    c3.metric("Available", available_rooms)

st.divider()

# --------------------------------------------------
# 🔍 FILTERING
# --------------------------------------------------
if "Hostel" in data.columns:
    hostels = sorted(data["Hostel"].dropna().unique())
    selected_hostel = st.selectbox("🏢 Filter by Hostel", ["All"] + hostels)
    df = data if selected_hostel == "All" else data[data["Hostel"] == selected_hostel]
else:
    selected_hostel = "All"
    df = data

# --------------------------------------------------
# 📊 TABLE + CHART
# --------------------------------------------------
st.subheader(f"📋 Room Summary — {selected_hostel}")
st.dataframe(df, use_container_width=True)

if "Hostel" in data.columns:
    st.subheader("📈 Bookings per Hostel")
    chart = data.groupby("Hostel")["Booked"].sum().reset_index()
    chart["Booked"] = chart["Booked"].astype(int)
    st.bar_chart(chart.set_index("Hostel"))

# --------------------------------------------------
# 📥 DOWNLOAD BUTTON (Excel)
# --------------------------------------------------
st.subheader("⬇️ Export Data")
to_download = df.to_excel(index=False, engine="openpyxl")
buffer = io.BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📤 Download Excel File",
    data=buffer,
    file_name=f"guest_room_dashboard_{selected_hostel.lower()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Powered by Streamlit • Live data from Google Sheets • Auto-refresh every 60s")
