import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="P&C CHO Vehicle Portal", layout="wide")

# --- BRANDING: RIL LOGO ---
st.image("https://upload.wikimedia.org/wikipedia/en/thumb/9/99/Reliance_Industries_Logo.svg/1200px-Reliance_Industries_Logo.svg.png", width=200)
st.title("🚗 P&C - CHO Departmental Vehicle Portal")
st.markdown("#### Reliance Industries Limited - Jamnagar Refinery")

# --- 1. SHARED DATABASE ---
@st.cache_resource
def get_global_database():
    return pd.DataFrame(columns=["Date", "Trip Category", "Car", "Main Passenger", "Accompanied By", "Destination", "Time"])

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
staff_list_with_guest = staff_list + ["External Guest"]

# --- 3. BOOKING ENGINE ---
st.subheader("📝 New Booking")
now = datetime.now()
today_str = now.strftime('%Y-%m-%d')

col1, col2 = st.columns(2)

with col1:
    trip_type = st.radio("Trip Category", ["Morning Pool Trip", "Evening Late Sitting Trip", "Ad-hoc Office Trip"])
    selected_car = st.selectbox("Select Car", ["Ertiga 1", "Ertiga 2"])
    
with col2:
    if trip_type == "Morning Pool Trip":
        roster_dates = [now.date() + timedelta(days=i) for i in range(7) if (now.date() + timedelta(days=i)).weekday() < 6]
        travel_date = st.selectbox("Select Date (Advance)", roster_dates)
    else:
        # Fixed to today for Evening and Ad-hoc
        travel_date = now.date()
        st.info(f"Booking for Today: {today_str}")

# Ad-hoc Companion Logic
companions = "Alone"
if trip_type == "Ad-hoc Office Trip":
    travel_mode = st.selectbox("Traveling Alone or with others?", ["Alone", "With Team Member/Guest"])
    if travel_mode == "With Team Member/Guest":
        selected_companions = st.multiselect("Select who is accompanying you:", staff_list_with_guest)
        companions = ", ".join(selected_companions) if selected_companions else "Alone"

# Occupancy Check
car_day_bookings = df_shared[(df_shared['Car'] == selected_car) & (df_shared['Date'] == str(travel_date))]
if len(car_day_bookings) >= 6:
    st.error(f"🚫 {selected_car} is FULL.")
    st.warning("⚠️ Contact Admin: **Samir Doshi (+91 90333 29720)**.")
else:
    with st.form("booking_form", clear_on_submit=True):
        c_a, c_b = st.columns(2)
        with c_a:
            p_name = st.selectbox("Your Name (Main Passenger)*", staff_list)
        with c_b:
            # Evening trip time logic
            default_time = now.time() if trip_type != "Evening Late Sitting Trip" else datetime.strptime("19:00", "%H:%M").time()
            time_val = st.time_input("Departure Time*", default_time)
            dest = st.text_input("Destination*")
            
        submit = st.form_submit_button("Confirm Booking")

        if submit:
            # Strict evening time check
            is_evening = (trip_type == "Evening Late Sitting Trip")
            evening_time_valid = time_val >= datetime.strptime("19:00", "%H:%M").time()
            
            if is_evening and not evening_time_valid:
                st.error("Evening Late Sitting trips can only be booked for departures at or after 07:00 PM.")
            elif not dest:
                st.error("Please provide a Destination.")
            else:
                new_row = [str(travel_date), trip_type, selected_car, p_name, companions, dest, time_val.strftime("%H:%M")]
                df_shared.loc[len(df_shared)] = new_row
                st.success(f"Booking confirmed for {p_name}!")
                st.rerun()

# --- 4. LIVE MANIFEST ---
st.divider()
st.subheader("📊 Live Travel Manifest")
view_date = st.date_input("View manifest for date:", now.date())
st.dataframe(df_shared[df_shared['Date'] == str(view_date)], use_container_width=True)

# --- 5. WEEKLY ROSTER VIEW (AT BOTTOM) ---
st.divider()
st.subheader("📅 Weekly Trip Occupancy")
roster_data = []
roster_dates_view = [now.date() + timedelta(days=i) for i in range(7) if (now.date() + timedelta(days=i)).weekday() < 6]

for d in roster_dates_view:
    d_str = str(d)
    e1_count = len(df_shared[(df_shared['Car'] == "Ertiga 1") & (df_shared['Date'] == d_str)])
    e2_count = len(df_shared[(df_shared['Car'] == "Ertiga 2") & (df_shared['Date'] == d_str)])
    roster_data.append({"Day": d.strftime("%A"), "Date": d_str, "Ertiga 1": f"{e1_count}/6", "Ertiga 2": f"{e2_count}/6"})

st.table(pd.DataFrame(roster_data))

# --- 6. ADMIN PORTAL ---
with st.expander("🔐 Admin Controls"):
    if st.text_input("Admin Password", type="password") == "Harish@1989#":
        if st.button("Clear All Data"):
            df_shared.drop(df_shared.index, inplace=True)
            st.rerun()
        st.download_button("📥 Download Excel", df_shared.to_csv(index=False).encode('utf-8'), "CHO_PC_Logs.csv")
