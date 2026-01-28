import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Dept Vehicle Booking", layout="wide")
st.title("📂 Departmental Vehicle Booking (Global Live)")

# --- 1. THE SHARED DATABASE ---
# This "cache" with allow_output_mutation=True acts as a shared global variable
@st.cache_resource
def get_global_database():
    # This only runs once when the app starts for the FIRST person
    return pd.DataFrame(columns=["Date", "Car", "Seat", "Name", "ID", "Destination", "Time", "Contact"])

# Get the shared data
df_shared = get_global_database()

# --- 2. SIDEBAR STATUS ---
st.sidebar.header("🚖 Real-Time Status")
sidebar_date = st.sidebar.date_input("Check occupancy for:", datetime.now().date())

drivers = {"Ertiga 1": "Rajesh (+91 98XXX-XXXXX)", "Ertiga 2": "Suresh (+91 97XXX-XXXXX)"}

for car, info in drivers.items():
    car_df = df_shared[(df_shared['Car'] == car) & (df_shared['Date'] == str(sidebar_date))]
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
    booked_seats = df_shared[(df_shared['Car'] == car_choice) & (df_shared['Date'] == datetime.now().strftime('%Y-%m-%d'))]['Seat'].tolist()
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
            # Directly update the shared global dataframe
            new_idx = len(df_shared)
            df_shared.loc[new_idx] = [
                str(date_val), car_choice, seat, name, emp_id, dest, time.strftime("%H:%M"), mobile
            ]
            st.success("Booking Saved for Everyone!")
            st.rerun()

# --- 4. LIVE MANIFEST ---
st.subheader("📋 Current Live Passenger List")
st.dataframe(df_shared[df_shared['Date'] == str(sidebar_date)], use_container_width=True)

# --- 5. ADMIN ---
with st.expander("🔐 Admin"):
    if st.text_input("Password", type="password") == "admin123":
        csv = df_shared.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master Record", csv, "cab_records.csv")
