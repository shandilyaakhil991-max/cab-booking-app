import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="P&C CHO Vehicle Portal", layout="wide")
st.title("🚗 P&C - CHO Departmental Vehicle Portal")
st.markdown("#### Reliance Industries Limited - Jamnagar Refinery")

# --- 1. SHARED DATABASE ---
@st.cache_resource
def get_global_database():
    # Central storage for all department travel records
    return pd.DataFrame(columns=["Date", "Trip Category", "Car", "Name", "Destination", "Time", "Contact"])

df_shared = get_global_database()

# --- 2. STAFF DIRECTORY ---
staff_list = sorted(list(set([
    "Akhil Kotadiya", "Akshay Saxena", "Alpesh5 Patel", "Bhargavkumar S", "Darshit Beladiya", 
    "Disha Sutariya", "Ghanshyam Dapkara", "Harish19 Sharma", "Hiral1 Trivedi", "Jaivik Shinde", 
    "Jay25 Patel", "Jigar1 Darji", "Jignesh Vador", "Jinal Desai", "Karan12 Patel", "Mayank14 Patel", 
    "Mixip Patel", "Nischal Ghosh", "Parthiv Bhatt", "Piyush Hirpara", "Pranjal Asati", "Pratik Lodhari", 
    "Rajesh6 Panchal", "Ramdevsinh Gohil", "Rasesh Vashi", "Ravi Desai", "Rohit21 Thakur", 
    "Roshan3 Shah", "Rut Bhatt", "Sagar Bhuva", "Samir R Doshi", "Sanju Mertia", "Shraddha1 V", 
    "Shreyansh Shah", "Tej Desai", "Vishal Buddh", "Vishal17 Shah", "Vivek1 Mehta", "Yash Popat", 
    "Yash1 Mistry", "Yashvi Vadwala", "Akhil Shandilya", "Hasmukh Morasiya", "Pankaj8 Pathak", 
    "Damu Shrao", "Chirag Bhavsar", "Bhargav Vachhani", "Nikunj K Patel", "Jigar3 Vyas", 
    "Anil K. Saklani", "Vishal Sutariya", "Dinesh3 Shinde", "Manish1 Tawade", "Gireesh Sagi", 
    "Karthikeyan10 K", "Sudheer Atmakur", "Anjani11 Kumar", "Sankaranarayanan A", "Mangesh Gawhale", 
    "Jagdish Charan", "Vaibhav Mahoday", "Muralikrishna T", "Chhunnulal2 Gupta", "Yogesh P Sonawane", 
    "Mahesh Bhaskar", "Rodi1 Choubisa", "Ketan Padh", "Samip Trivedi", "Upamanyu Mehta", 
    "Jignesh Shah", "Pradip Karia"
])))

# --- 3. WEEKLY ROSTER VIEW ---
st.subheader("📅 Weekly Trip Roster")
today = datetime.now().date()
# Generate Monday-Saturday dates for the current week
roster_dates = [today + timedelta(days=i) for i in range(7) if (today + timedelta(days=i)).weekday() < 6]
roster_data = []

for d in roster_dates:
    d_str = str(d)
    e1_count = len(df_shared[(df_shared['Car'] == "Ertiga 1") & (df_shared['Date'] == d_str)])
    e2_count = len(df_shared[(df_shared['Car'] == "Ertiga 2") & (df_shared['Date'] == d_str)])
    roster_data.append({"Day": d.strftime("%A"), "Date": d_str, "Ertiga 1 Bookings": e1_count, "Ertiga 2 Bookings": e2_count})

st.table(pd.DataFrame(roster_data))

# --- 4. BOOKING ENGINE ---
st.divider()
st.subheader("📝 New Booking")

col1, col2 = st.columns(2)

with col1:
    trip_type = st.radio("Trip Category", ["Morning Pool Trip", "Evening Late Sitting Trip", "Random Office Booking"])
    selected_car = st.selectbox("Select Car", ["Ertiga 1", "Ertiga 2"])
    
with col2:
    if trip_type == "Morning Pool Trip":
        travel_date = st.selectbox("Select Date (Mon-Sat Advance)", roster_dates)
    else:
        travel_date = st.date_input("Travel Date", today)

# Validation for Evening Trip (Post 7 PM)
evening_valid = True
if trip_type == "Evening Late Sitting Trip":
    st.info("Note: Evening pool trips are only available for departures post 07:00 PM.")

# Occupancy Check
car_day_bookings = df_shared[(df_shared['Car'] == selected_car) & (df_shared['Date'] == str(travel_date))]
if len(car_day_bookings) >= 6:
    st.error(f"🚫 {selected_car} is FULL for {travel_date}.")
    st.warning("⚠️ Contact Admin: **Samir Doshi (+91 90333 29720)**.")
else:
    with st.form("booking_form", clear_on_submit=True):
        c_a, c_b = st.columns(2)
        with c_a:
            p_name = st.selectbox("Select Name*", staff_list)
            contact = st.text_input("Mobile Number*")
        with c_b:
            time_val = st.time_input("Departure Time*", datetime.now().time())
            dest = st.text_input("Destination*")
            
        if st.form_submit_button("Confirm Booking"):
            # Time check for evening trip
            if trip_type == "Evening Late Sitting Trip" and time_val < datetime.strptime("19:00", "%H:%M").time():
                st.error("Evening pool trips must start at or after 07:00 PM.")
            elif not contact or not dest:
                st.error("Please fill all mandatory fields (*).")
            else:
                new_data = [str(travel_date), trip_type, selected_car, p_name, dest, time_val.strftime("%H:%M"), contact]
                df_shared.loc[len(df_shared)] = new_data
                st.success(f"Successfully booked {selected_car} for {p_name}!")
                st.rerun()

# --- 5. DEPARTMENTAL MANIFEST ---
st.divider()
st.subheader("📊 Live Travel Manifest")
view_date = st.date_input("View manifest for date:", today)
st.dataframe(df_shared[df_shared['Date'] == str(view_date)], use_container_width=True)

# --- 6. ADMIN PORTAL ---
with st.expander("🔐 Admin Controls"):
    if st.text_input("Admin Password", type="password") == "Harish@1989#":
        if st.button("Clear All Data"):
            df_shared.drop(df_shared.index, inplace=True)
            st.rerun()
        csv = df_shared.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master Excel", csv, "PC_CHO_Travel_Log.csv")
