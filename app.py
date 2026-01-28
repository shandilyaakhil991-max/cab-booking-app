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

# --- SIDEBAR: LIVE OCCUPANCY ---
st.sidebar.header("🚖 Real-Time Status")
# We filter the sidebar by the current date being viewed
sidebar_date = st.sidebar.date_input("Check occupancy for:", datetime.now().date())

for car, info in drivers.items():
    # COUNT ONLY BOOKINGS FOR THE SELECTED DATE
    car_df = st.session_state.bookings[
        (st.session_state.bookings['Car'] == car) & 
        (st.session_state.bookings['Date'] == sidebar_date)
    ]
    occupancy = len(car_df)
    
    st.sidebar.subheader(f"{car}")
    st.sidebar.write(f"👤 {info['Name']} | 📞 {info['Phone']}")
    st.sidebar.progress(occupancy / 6) # Visual progress bar
    st.sidebar.write(f"💺 Occupied: {occupancy}/6")
    
    if not car_df.empty:
        st.sidebar.warning(f"⏰ Last Dept: {car_df['Time'].max()}")
    st.sidebar.markdown("---")

# --- MAIN BOOKING FORM ---
with st.expander("➕ Click Here to Book a Seat", expanded=True):
    with st.form("booking_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            date_val = st.date_input("Travel Date", datetime.now().date())
            req_name = st.text_input("Name*")
            req_id = st.text_input("Employee ID*")
        with c2:
            car_choice = st.selectbox("Vehicle", ["Ertiga 1", "Ertiga 2"])
            contact = st.text_input("Mobile No.*")
            dep_time = st.time_input("Departure Time")
        with c3:
            all_seats = ["Front", "Middle Left", "Middle Center", "Middle Right", "Rear Left", "Rear Right"]
            # Important: Filter seats based on car AND date
            booked_seats = st.session_state.bookings[
                (st.session_state.bookings['Car'] == car_choice) & 
                (st.session_state.bookings['Date'] == date_val)
            ]['Seat'].tolist()
            available_seats = [s for s in all_seats if s not in booked_seats]
            seat_choice = st.selectbox("Seat Preference", available_seats if available_seats else ["FULL"])
            dest = st.text_input("Drop Location")

        if st.form_submit_button("Confirm Booking"):
            if not req_name or not req_id or not contact:
                st.error("Missing required fields!")
            elif seat_choice == "FULL":
                st.error("No seats left in this car!")
            else:
                new_row = pd.DataFrame([[
                    date_val, car_choice, seat_choice, req_name, req_id, dest, dep_time.strftime("%H:%M"), contact
                ]], columns=st.session_state.bookings.columns)
                st.session_state.bookings = pd.concat([st.session_state.bookings, new_row], ignore_index=True)
                st.success(f"Success! {req_name} booked {seat_choice} in {car_choice}.")
                st.rerun() # Force sidebar to update immediately

# --- MANIFEST FOR COORDINATION ---
st.subheader("📋 Current Passenger List")
view_df = st.session_state.bookings[st.session_state.bookings['Date'] == sidebar_date]
if not view_df.empty:
    st.dataframe(view_df[["Car", "Seat", "Name", "Time", "Destination", "Contact"]], use_container_width=True)
    
    # Simple Coordination Helper
    st.info("💡 Coordinate: You can see your peers' mobile numbers above to coordinate departure.")
else:
    st.write("No bookings recorded for this date yet.")

# --- DATA COLLECTION (EXCEL/CSV) ---
st.markdown("---")
with st.expander("🔐 Admin Login (For Data Record Collection)"):
    pw = st.text_input("Enter Admin Password", type="password")
    if pw == "admin123":
        st.write("### Master Record (All Dates)")
        st.dataframe(st.session_state.bookings)
        csv_data = st.session_state.bookings.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Master Excel (CSV)",
            data=csv_data,
            file_name=f"department_cab_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
