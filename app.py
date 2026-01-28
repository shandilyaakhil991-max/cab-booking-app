import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dept Vehicle Booking", page_icon="🚗", layout="wide")
st.markdown("## 📂 Departmental Vehicle Booking")

# --- 1. CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch fresh data
try:
    df = conn.read(ttl=0)
except:
    df = pd.DataFrame(columns=["Date", "Car", "Seat", "Name", "ID", "Destination", "Time", "Contact"])

# Driver Info
drivers = {"Ertiga 1": "Rajesh (+91 98XXX-XXXXX)", "Ertiga 2": "Suresh (+91 97XXX-XXXXX)"}

# --- 2. SIDEBAR STATUS ---
st.sidebar.header("🚖 Real-Time Status")
sidebar_date = st.sidebar.date_input("Check date:", datetime.now().date())

for car, info in drivers.items():
    car_df = df[(df['Car'] == car) & (df['Date'] == str(sidebar_date))]
    occ = len(car_df)
    st.sidebar.subheader(f"{car}")
    st.sidebar.write(f"👤 {info}")
    st.sidebar.progress(min(occ / 6, 1.0))
    st.sidebar.write(f"💺 Occupied: {occ}/6")
    st.sidebar.markdown("---")

# --- 3. BOOKING FORM ---
st.subheader("➕ Make a New Booking")
car_choice = st.selectbox("1. Select Vehicle*", ["--- Select Vehicle ---", "Ertiga 1", "Ertiga 2"])

all_seats = ["Front", "Middle Left", "Middle Center", "Middle Right", "Rear Left", "Rear Right"]
if car_choice != "--- Select Vehicle ---":
    booked_seats = df[(df['Car'] == car_choice) & (df['Date'] == datetime.now().strftime('%Y-%m-%d'))]['Seat'].tolist()
    available_seats = [s for s in all_seats if s not in booked_seats]
else:
    available_seats = []

with st.form("booking_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        date_val = st.date_input("Travel Date*", datetime.now().date())
        name = st.text_input("Name*")
        emp_id = st.text_input("Employee ID*")
    with c2:
        seat = st.selectbox("2. Seat Preference*", available_seats if available_seats else ["FULL"])
        mobile = st.text_input("Mobile No.*")
        time = st.time_input("Departure Time*")
    
    dest = st.text_input("Drop Location*")
    submit = st.form_submit_button("Confirm Booking")

    if submit:
        if car_choice == "--- Select Vehicle ---" or not name or not dest:
            st.error("Please fill all mandatory fields.")
        else:
            new_row = pd.DataFrame([{
                "Date": str(date_val), "Car": car_choice, "Seat": seat,
                "Name": name, "ID": emp_id, "Destination": dest,
                "Time": time.strftime("%H:%M"), "Contact": mobile
            }])
            # UPDATE LOGIC
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Booking Sync Successful!")
            st.rerun()

# --- 4. LIVE MANIFEST ---
st.subheader("📋 Current Live Passenger List")
st.dataframe(df[df['Date'] == str(sidebar_date)], use_container_width=True)

# --- 5. ADMIN ---
with st.expander("🔐 Admin"):
    if st.text_input("Password", type="password") == "admin123":
        st.download_button("📥 Download Excel", df.to_csv(index=False), "cab_logs.csv")
