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
    return pd.DataFrame(columns=["Date", "Trip Category", "Car", "Name", "Destination", "Time", "Contact"])

df_shared = get_global_database()

# --- 2. STAFF DIRECTORY (Cleaned List) ---
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
    "Mahesh Bhaskar", "Rodi1 Choubisa", "Ketan Padh", "Samip Trivedi", "Manishkumar K", 
    "Upamanyu Mehta", "Jignesh Shah", "Pradip Karia"
])))

# --- 3. LOGIN & DASHBOARD ---
st.sidebar.header("👤 User Dashboard")
user_name = st.sidebar.selectbox("Select Your Name to Login", ["--- Guest ---"] + staff_list)

if user_name != "--- Guest ---":
    st.sidebar.success(f"Welcome, {user_name}")
    user_bookings = df_shared[df_shared['Name'] == user_name]
    
    st.sidebar.subheader("My Upcoming Trips")
    if not user_bookings.empty:
        st.sidebar.dataframe(user_bookings[["Date", "Trip Category", "Time"]], hide_index=True)
    else:
        st.sidebar.write("No active bookings found.")

# --- 4. BOOKING ENGINE ---
st.subheader("📝 Book a Vehicle")

col1, col2 = st.columns(2)

with col1:
    trip_type = st.radio("Trip Category", ["Morning Pool Trip", "Evening Late Sitting Trip", "Random Office Booking"])
    selected_car = st.selectbox("Select Car", ["Ertiga 1", "Ertiga 2"])
    
with col2:
    if trip_type == "Morning Pool Trip":
        # Allow booking for upcoming week (Mon-Sat)
        today = datetime.now().date()
        next_week = [today + timedelta(days=i) for i in range(7) if (today + timedelta(days=i)).weekday() < 6]
        travel_date = st.selectbox("Select Date (Mon-Sat)", next_week)
    else:
        travel_date = st.date_input("Travel Date", datetime.now().date())

# Occupancy Check
car_day_bookings = df_shared[(df_shared['Car'] == selected_car) & (df_shared['Date'] == str(travel_date))]
occ = len(car_day_bookings)

if occ >= 6:
    st.error(f"🚫 {selected_car} is FULL.")
    st.warning("⚠️ Contact Admin: **Samir Doshi (+91 90333 29720)** for arrangements.")
else:
    with st.form("main_booking_form", clear_on_submit=True):
        c_a, c_b = st.columns(2)
        with c_a:
            name_confirm = st.selectbox("Confirm Your Name*", staff_list)
            contact = st.text_input("Mobile Number*")
        with c_b:
            time_val = st.time_input("Preferred Time", datetime.now().time())
            dest = st.text_input("Destination/Drop Point*")
            
        if st.form_submit_button("Confirm My Booking"):
            if not contact or not dest:
                st.error("Please provide Mobile No. and Destination.")
            else:
                new_data = [str(travel_date), trip_type, selected_car, name_confirm, dest, time_val.strftime("%H:%M"), contact]
                df_shared.loc[len(df_shared)] = new_data
                st.success(f"Booking confirmed for {name_confirm}!")
                st.rerun()

# --- 5. DEPARTMENTAL REPORTS ---
st.divider()
st.subheader("📊 Departmental Travel Report")
tab1, tab2, tab3 = st.tabs(["Morning Pool", "Evening Late Sitting", "Random Office"])

with tab1:
    st.dataframe(df_shared[df_shared['Trip Category'] == "Morning Pool Trip"], use_container_width=True)
with tab2:
    st.dataframe(df_shared[df_shared['Trip Category'] == "Evening Late Sitting Trip"], use_container_width=True)
with tab3:
    st.dataframe(df_shared[df_shared['Trip Category'] == "Random Office Booking"], use_container_width=True)

# --- 6. ADMIN PORTAL ---
st.divider()
with st.expander("🔐 Admin Control Panel"):
    admin_pw = st.text_input("Admin Password", type="password")
    if admin_pw == "Harish@1989#": #
        st.write("### Master Records (All Trips)")
        st.dataframe(df_shared)
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            if st.button("Reset Global Database"):
                df_shared.drop(df_shared.index, inplace=True)
                st.rerun()
        with col_res2:
            csv = df_shared.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Master Excel", csv, "P&C_Vehicle_Logs.csv")
