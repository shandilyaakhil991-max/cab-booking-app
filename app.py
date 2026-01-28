import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Dept Vehicle Booking", layout="wide")
st.title("📂 Departmental Vehicle Booking")

# --- 1. SHARED DATABASE ---
@st.cache_resource
def get_global_database():
    # Global storage shared across all office devices
    return pd.DataFrame(columns=["Date", "Car", "Seat", "Name", "ID", "Destination", "Time", "Contact"])

df_shared = get_global_database()

# --- 2. SIDEBAR STATUS ---
st.sidebar.header("🚖 Real-Time Status")
sidebar_date = st.sidebar.date_input("Check occupancy for:", datetime.now().date())

drivers = {"Ertiga 1": "Rajesh (+91 98XXX-XXXXX)", "Ertiga 2": "Suresh (+91 97XXX-XXXXX)"}

# Track which cars are full for the selected sidebar date
full_cars = []

for car, info in drivers.items():
    car_df = df_shared[(df_shared['Car'] == car) & (df_shared['Date'] == str(sidebar_date))]
    occ = len(car_df)
    
    if occ >= 6:
        full_cars.append(car)
    
    st.sidebar.subheader(f"{car}")
    st.sidebar.write(f"👤 {info}")
    st.sidebar.progress(min(occ / 6, 1.0))
    st.sidebar.write(f"💺 Occupied: {occ}/6")
    st.sidebar.markdown("---")

# --- 3. BOOKING FORM ---
st.subheader("➕ Make a New Booking")
car_choice = st.selectbox("1. Select Vehicle*", ["--- Select Vehicle ---", "Ertiga 1", "Ertiga 2"])

# Check if selected car is full
if car_choice in full_cars:
    st.error(f"🚫 {car_choice} is FULLY BOOKED.")
    st.warning("⚠️ Please contact Admin: **Samir Doshi (+91 90333 29720)** for arranging another vehicle as this is booked.")
else:
    all_seats = ["Front", "Middle Left", "Middle Center", "Middle Right", "Rear Left", "Rear Right"]
    available_seats = []

    if car_choice != "--- Select Vehicle ---":
        # Check bookings for the travel date entered in the form
        current_date_str = datetime.now().strftime('%Y-%m-%d')
        booked_seats = df_shared[(df_shared['Car'] == car_choice) & (df_shared['Date'] == current_date_str)]['Seat'].tolist()
        available_seats = [s for s in all_seats if s not in booked_seats]

    with st.form("booking_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date_val = st.date_input("Travel Date*", datetime.now().date())
            req_name = st.text_input("Name*")
            req_id = st.text_input("Employee ID*")
        with c2:
            seat = st.selectbox("2. Seat Preference*", available_seats if available_seats else ["Select Vehicle First"])
            mobile = st.text_input("Mobile No.*")
            time = st.time_input("Departure Time*")
        
        dest = st.text_input("Drop Location*")
        submit = st.form_submit_button("Confirm Booking")

        if submit:
            if car_choice == "--- Select Vehicle ---" or not req_name or not dest:
                st.error("Please fill all mandatory fields.")
            else:
                new_idx = len(df_shared)
                df_shared.loc[new_idx] = [str(date_val), car_choice, seat, req_name, req_id, dest, time.strftime("%H:%M"), mobile]
                st.success("Booking Saved! The list has been updated for all devices.")
                st.rerun()

# --- 4. LIVE MANIFEST ---
st.subheader("📋 Current Live Passenger List")
view_df = df_shared[df_shared['Date'] == str(sidebar_date)]
if not view_df.empty:
    st.dataframe(view_df[["Car", "Seat", "Name", "Time", "Destination", "Contact"]], use_container_width=True)
else:
    st.info("No bookings recorded for this date yet.")

# --- 5. ADMIN RESET CONTROLS ---
st.markdown("---")
with st.expander("🔐 Admin Controls (Reset & Data Collection)"):
    # Updated Password
    pw = st.text_input("Enter Admin Password", type="password")
    if pw == "Harish@1989#":
        st.write("### Trip Management")
        st.info("Resetting a vehicle will clear its seat list to allow a fresh round of 6 bookings.")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("Reset Ertiga 1 (New Trip)"):
                indices = df_shared[(df_shared['Car'] == "Ertiga 1") & (df_shared['Date'] == str(sidebar_date))].index
                df_shared.drop(indices, inplace=True)
                st.success("Ertiga 1 reset successfully.")
                st.rerun()
        with col_r2:
            if st.button("Reset Ertiga 2 (New Trip)"):
                indices = df_shared[(df_shared['Car'] == "Ertiga 2") & (df_shared['Date'] == str(sidebar_date))].index
                df_shared.drop(indices, inplace=True)
                st.success("Ertiga 2 reset successfully.")
                st.rerun()

        st.write("### Procurement Data Records")
        csv = df_shared.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master CSV for Excel", csv, f"cab_logs_{sidebar_date}.csv")
