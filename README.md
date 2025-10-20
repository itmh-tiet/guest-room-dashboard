# 🏨 Thapar Guest Room Dashboard

A live analytics dashboard for Thapar Institute's Guest Room booking system, built with **Streamlit** and connected to **Google Sheets**.

## 🔧 Features
- Real-time Google Sheets integration (via service account)
- Auto-refresh every 60 seconds
- Summary cards for Total / Booked / Available rooms
- Filter by hostel
- Interactive charts (bar and line)
- Secure deployment using Streamlit Secrets

## 🗂️ Files
| File | Description |
|------|--------------|
| `dashboard.py` | Main Streamlit app |
| `requirements.txt` | Python dependencies |
| `README.md` | About this project |

## 🚀 Deployment
Deployed via [Streamlit Cloud](https://streamlit.io/cloud).  
To deploy your own version:
1. Fork this repo
2. Add your Google Service Account JSON to Streamlit Secrets as `CREDS_JSON`
3. Deploy via Streamlit Cloud.

---

💡 **Developed by:** Navjot Sharma  
📅 **Updated:** October 2025
