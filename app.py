import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Dept Vehicle Booking", page_icon="🚗", layout="wide")
st.markdown("## 📂 Departmental Vehicle Booking")

# --- INITIALIZE DATABASE ---
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=[
        "Date", "Car", "Seat", "Name", "ID", "Destination", "Time", "Contact"
    ])

drivers = {
    "Ertiga 1": {"Name": "Rajesh Kumar", "Phone": "+91 98XXX-XXXXX"},
    "Ertiga 2": {"Name": "Suresh Singh", "Phone": "+91 97XXX-XXXXX"}
}

# --- SIDEBAR: LIVE STATUS ---
st.sidebar.header("🚖 Real-Time Status")
sidebar_date = st.sidebar.date_input("Check occupancy for:", datetime.now().date())

for car, info in drivers.items():
    car_df = st.session_state.bookings[
        (st.session_state.bookings['Car'] == car) & 
        (st.session_state.bookings['Date'] == sidebar_date)
    ]
    occupancy = len(car_df)
    st.sidebar.subheader(f"{car}")
    st.sidebar.write(f"👤 {info['Name']} | 📞 {info['Phone']}")
    st.sidebar.progress(occupancy / 6)
    st.sidebar.write(f"💺 Occupied: {occupancy}/6")
    if not car_df.empty:
        st.sidebar.warning(f"⏰ Last Dept: {car_df['Time'].max()}")
    st.sidebar.markdown("---")

# --- MAIN BOOKING FORM ---
st.subheader("➕ Make a New Booking")

# Step 1: Pick the Car (OUTSIDE the form so it refreshes the seat list immediately)
car_choice = st.selectbox("1. Select Vehicle*", ["--- Select Vehicle ---", "Ertiga 1", "Ertiga 2"])

# Step 2: Calculate available seats based on choice
all_seats = ["Front", "Middle Left", "Middle Center", "Middle Right", "Rear Left", "Rear Right"]
available_seats = []

if car_choice != "--- Select Vehicle ---":
    booked_seats = st.session_state.bookings[
        (st.session_state.bookings['Car'] == car_choice) & 
        (st.session_state.bookings['Date'] == datetime.now().date())
    ]['Seat'].tolist()
    available_seats = [s for s in all_seats if s not in booked_seats]
else:
    st.warning("Please select a vehicle above to see available seats.")

# Step 3: The Rest of the Details in a Form
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
    
    dest = st.text_input("Drop Location*")
    
    submit = st.form_submit_button("Confirm Booking")

    if submit:
        if car_choice == "--- Select Vehicle ---":
            st.error("Please select a vehicle first.")
        elif not req_name or not req_id or not contact or not dest:
            st.error("All fields marked * are mandatory.")
        elif seat_choice == "FULL":
            st.error("No seats available in this vehicle.")
        else:
            new_row = pd.DataFrame([[
                date_val, car_choice, seat_choice, req_name, req_id, dest, dep_time.strftime("%H:%M"), contact
            ]], columns=st.session_state.bookings.columns)
            st.session_state.bookings = pd.concat([st.session_state.bookings, new_row], ignore_index=True)
            st.success(f"Success! {req_name} booked {seat_choice} in {car_choice}.")
            st.rerun()

# --- MANIFEST ---
st.subheader("📋 Current Passenger List")
view_df = st.session_state.bookings[st.session_state.bookings['Date'] == sidebar_date]
if not view_df.empty:
    st.dataframe(view_df[["Car", "Seat", "Name", "Time", "Destination", "Contact"]], use_container_width=True)
else:
    st.write("No bookings recorded yet.")

# --- ADMIN ---
st.markdown("---")
with st.expander("🔐 Admin Login"):
    pw = st.text_input("Password", type="password")
    if pw == "admin123":
        st.dataframe(st.session_state.bookings)
        csv = st.session_state.bookings.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master CSV", data=csv, file_name="cab_records.csv")
