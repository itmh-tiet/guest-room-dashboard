import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---- Google Sheets connection ----
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Hg7B61fUjouI_-R0bSm2aFxqM_gI89QlXZoNAFJYi1w"
sheet = client.open_by_url(SPREADSHEET_URL).worksheet("Guest Room Dashboard")
data = pd.DataFrame(sheet.get_all_records())

# ---- Data prep ----
data.columns = [c.strip().title() for c in data.columns]
data["Booked"] = data.apply(
    lambda r: any("BOOKED" in str(v).upper() for v in r.values), axis=1
)

total_rooms = len(data)
booked_rooms = data["Booked"].sum()
available_rooms = total_rooms - booked_rooms

# ---- Streamlit UI ----
st.set_page_config(page_title="Thapar Guest Room Dashboard", page_icon="🏨", layout="wide")
st.title("🏨 Thapar Guest Room Dashboard")

c1, c2, c3 = st.columns(3)
c1.metric("Total Rooms", total_rooms)
c2.metric("Booked", booked_rooms)
c3.metric("Available", available_rooms)

hostels = sorted(data["Hostel"].unique()) if "Hostel" in data.columns else []
selected_hostel = st.selectbox("Filter by Hostel", ["All"] + hostels)
df = data if selected_hostel == "All" else data[data["Hostel"] == selected_hostel]
st.dataframe(df, use_container_width=True)

st.subheader("Bookings per Hostel")
if "Hostel" in data.columns:
    chart = data.groupby("Hostel")["Booked"].sum().reset_index()
    chart["Booked"] = chart["Booked"].astype(int)
    st.bar_chart(chart.set_index("Hostel"))

st.caption("Powered by Streamlit • Live data from Google Sheets")
