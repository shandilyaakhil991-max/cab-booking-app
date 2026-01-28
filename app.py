import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dept Vehicle Booking", page_icon="🚗", layout="wide")

# Header as requested
st.title("📂 Departmental Vehicle Booking")
st.info("Note: Company buses depart at 6:55 PM. Use this for late-night coordination.")

# 1. Initialize Data
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=[
        "Date", "Car", "Seat", "Name", "ID", "Destination", "Time", "Contact"
    ])

# Driver Details
drivers = {
    "Ertiga 1": {"Name": "Rajesh Kumar", "Phone": "+91 98XXX-XXXXX"},
    "Ertiga 2": {"Name": "Suresh Singh", "Phone": "+91 97XXX-XXXXX"}
}

# 2. Sidebar for Status & Coordination
st.sidebar.header("🚖 Cab Status & Drivers")
for car, info in drivers.items():
    booked_count = len(st.session_state.bookings[st.session_state.bookings['Car'] == car])
    st.sidebar.subheader(f"{car}")
    st.sidebar.write(f"👤 **Driver:** {info['Name']}")
    st.sidebar.write(f"📞 **Call:** {info['Phone']}")
    st.sidebar.write(f"💺 **Occupied:** {booked_count}/6 seats")
    
    # Show last booking time for this car
    car_times = st.session_state.bookings[st.session_state.bookings['Car'] == car]['Time']
    if not car_times.empty:
        st.sidebar.warning(f"⏰ Last Departure: {max(car_times)}")
    st.sidebar.markdown("---")

# 3. Booking Form
with st.expander("➕ Make a New Booking", expanded=True):
    with st.form("booking_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date_val = st.date_input("Date", datetime.now())
            req_name = st.text_input("Your Name*")
            req_id = st.text_input("Employee ID*")
        with col2:
            car_choice = st.selectbox("Select Vehicle", ["Ertiga 1", "Ertiga 2"])
            contact = st.text_input("Your Mobile No. (for coordination)")
            dep_time = st.time_input("Your Departure Time")
        with col3:
            # Define specific seats
            all_seats = ["Front", "Middle Left", "Middle Center", "Middle Right", "Rear Left", "Rear Right"]
            # Filter out already booked seats for the selected car
            booked_seats = st.session_state.bookings[st.session_state.bookings['Car'] == car_choice]['Seat'].tolist()
            available_seats = [s for s in all_seats if s not in booked_seats]
            
            seat_choice = st.selectbox("Choose Available Seat", available_seats if available_seats else ["FULL"])
            dest = st.text_input("Drop Location")

        submit = st.form_submit_button("Confirm Booking")

        if submit:
            if seat_choice == "FULL":
                st.error("This vehicle is fully booked!")
            elif not req_name or not req_id:
                st.error("Please fill required fields.")
            else:
                new_entry = pd.DataFrame([[
                    date_val, car_choice, seat_choice, req_name, req_id, dest, dep_time.strftime("%H:%M"), contact
                ]], columns=st.session_state.bookings.columns)
                st.session_state.bookings = pd.concat([st.session_state.bookings, new_entry], ignore_index=True)
                st.success(f"Seat {seat_choice} confirmed in {car_choice}!")

# 4. Main Display for Coordination
st.subheader("📋 Current Booking Manifest (Coordinate with Peers)")
if not st.session_state.bookings.empty:
    # Stylized view for coordination
    for car in ["Ertiga 1", "Ertiga 2"]:
        st.write(f"### {car} Passengers")
        car_df = st.session_state.bookings[st.session_state.bookings['Car'] == car]
        if car_df.empty:
            st.write("No bookings yet.")
        else:
            st.dataframe(car_df[["Seat", "Name", "Time", "Destination", "Contact"]], use_container_width=True)
else:
    st.write("No bookings recorded today.")

# Download Button
if not st.session_state.bookings.empty:
    csv = st.session_state.bookings.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Final List for Admin", data=csv, file_name="cab_manifest.csv")
