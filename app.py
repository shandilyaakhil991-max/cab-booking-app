import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Dept Vehicle Booking", page_icon="🚗", layout="wide")
st.markdown("## 📂 Departmental Vehicle Booking")
st.info("Buses depart at 6:55 PM. Use this app for late-night coordination.")

# --- 2. CONNECT TO GOOGLE SHEETS ---
# This uses the URL you provided in the Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the live data
try:
    df = conn.read(ttl="0")
except Exception:
    # Fallback if sheet is empty/new
    df = pd.DataFrame(columns=["Date", "Car", "Seat", "Name", "ID", "Destination", "Time", "Contact"])

# Driver Details
drivers = {
    "Ertiga 1": {"Name": "Rajesh Kumar", "Phone": "+91 98XXX-XXXXX"},
    "Ertiga 2": {"Name": "Suresh Singh", "Phone": "+91 97XXX-XXXXX"}
}

# --- 3. SIDEBAR: LIVE STATUS ---
st.sidebar.header("🚖 Real-Time Status")
sidebar_date = st.sidebar.date_input("Check occupancy for:", datetime.now().date())

for car, info in drivers.items():
    # Filter live data for the sidebar count
    car_df = df[(df['Car'] == car) & (pd.to_datetime(df['Date']).dt.date == sidebar_date)]
    occupancy = len(car_df)
    
    st.sidebar.subheader(f"{car}")
    st.sidebar.write(f"👤 {info['Name']} | 📞 {info['Phone']}")
    st.sidebar.progress(min(occupancy / 6, 1.0))
    st.sidebar.write(f"💺 Occupied: {occupancy}/6")
    if not car_df.empty:
        st.sidebar.warning(f"⏰ Last Dept: {car_df['Time'].max()}")
    st.sidebar.markdown("---")

# --- 4. MAIN BOOKING FORM ---
st.subheader("➕ Make a New Booking")

# Step A: Select Vehicle (Outside form to trigger seat refresh)
car_choice = st.selectbox("1. Select Vehicle*", ["--- Select Vehicle ---", "Ertiga 1", "Ertiga 2"])

# Step B: Filter available seats
all_seats = ["Front", "Middle Left", "Middle Center", "Middle Right", "Rear Left", "Rear Right"]
available_seats = []

if car_choice != "--- Select Vehicle ---":
    # Get seats already taken for THIS car on THIS date
    booked_seats = df[
        (df['Car'] == car_choice) & 
        (pd.to_datetime(df['Date']).dt.date == datetime.now().date())
    ]['Seat'].tolist()
    available_seats = [s for s in all_seats if s not in booked_seats]
else:
    st.warning("Please select a vehicle to see available seats.")

# Step C: The Form
with st.form("booking_details", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        date_val = st.date_input("Travel Date*", datetime.now().date())
        req_name = st.text_input("Name*")
        req_id = st.text_input("Employee ID*")
    with c2:
        seat_choice = st.selectbox("2. Seat Preference*", available_seats if available_seats else ["FULL"])
        contact = st.text_input("Mobile No.*")
        dep_time = st.time_input("Departure Time*")
    
    dest = st.text_input("Drop Location* (Mandatory)")
    
    submit = st.form_submit_button("Confirm Booking")

    if submit:
        if car_choice == "--- Select Vehicle ---":
            st.error("Please select a vehicle.")
        elif not req_name or not req_id or not contact or not dest:
            st.error("All fields marked * are mandatory.")
        elif seat_choice == "FULL":
            st.error("No seats left in this car.")
        else:
            # Prepare new row
            new_row = pd.DataFrame([{
                "Date": date_val.strftime("%Y-%m-%d"),
                "Car": car_choice,
                "Seat": seat_choice,
                "Name": req_name,
                "ID": req_id,
                "Destination": dest,
                "Time": dep_time.strftime("%H:%M"),
                "Contact": contact
            }])
            
            # Update Google Sheet
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"Booking Sync Complete! {req_name} is confirmed.")
            st.rerun()

# --- 5. LIVE PASSENGER LIST ---
st.subheader("📋 Live Passenger Manifest")
view_df = df[pd.to_datetime(df['Date']).dt.date == sidebar_date]
if not view_df.empty:
    st.dataframe(view_df[["Car", "Seat", "Name", "Time", "Destination", "Contact"]], use_container_width=True)
else:
    st.write("No bookings found for this date.")

# --- 6. ADMIN SECTION ---
st.markdown("---")
with st.expander("🔐 Admin Access"):
    pw = st.text_input("Password", type="password")
    if pw == "admin123":
        st.write("### All History")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master CSV for Excel", data=csv, file_name="cab_records.csv")
