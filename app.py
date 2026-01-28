import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Late Night Cab", page_icon="🚖")

st.title("🚖 Dept. Late Night Cab Booking")
st.info("Buses stop at 6:55 PM. Use this to book your Ertiga seat.")

# Initialize a 'database' in the app memory
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["ID", "Name", "Car", "Seat", "Destination", "Time"])

# --- Booking Form ---
with st.form("booking_form"):
    col1, col2 = st.columns(2)
    with col1:
        req_id = st.text_input("Requisitioner ID")
        name = st.text_input("Name")
    with col2:
        car = st.selectbox("Select Ertiga", ["Ertiga 1", "Ertiga 2"])
        seat = st.selectbox("Seat", ["Front", "Middle", "Rear"])
    
    dest = st.text_input("Drop Location")
    time = st.time_input("Departure Time", value=datetime.strptime("19:00", "%H:%M").time())
    
    if st.form_submit_button("Confirm Booking"):
        new_entry = pd.DataFrame([[req_id, name, car, seat, dest, time.strftime("%H:%M")]], 
                                 columns=["ID", "Name", "Car", "Seat", "Destination", "Time"])
        st.session_state.bookings = pd.concat([st.session_state.bookings, new_entry], ignore_index=True)
        st.success(f"Seat booked for {name}!")

# --- Display Current Bookings ---
st.subheader("Today's Booking List")
st.table(st.session_state.bookings)
