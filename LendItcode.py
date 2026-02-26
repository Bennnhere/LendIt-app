import streamlit as st
import time
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="LendIt - Campus Rental", layout="centered")

# --- CUSTOM CSS FOR BETTER LOOKS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_value=True)

# --- MOCK DATABASE (Stored in Session State) ---
if 'items' not in st.session_state:
    st.session_state.items = [
        {"id": 1, "name": "Engineering Drafter", "owner": "Senior Rahul", "price": 10, "status": "Available"},
        {"id": 2, "name": "Lab Coat (Size M)", "owner": "Ananya (3rd Yr)", "price": 5, "status": "Available"},
        {"id": 3, "name": "Scientific Calculator", "owner": "Siddharth", "price": 15, "status": "Available"}
    ]
if 'active_rental' not in st.session_state:
    st.session_state.active_rental = None

# --- UI HEADER ---
st.title("🎓 LendIt")
st.caption("Peer-to-Peer Micro-Rentals for Campus Essentials")

# --- TAB NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🛍️ Borrow", "📤 Lend", "⏱️ Rental Status"])

# --- TAB 1: BORROW ---
with tab1:
    # THE "I'M COOKED" BUTTON
    if st.button("🚨 I'M COOKED (Emergency Broadcast)"):
        st.toast("Broadcasting your need to everyone in the hostel...")
        st.error("Emergency Alert Sent: Someone needs stationery at the Lab!")

    st.write("### Available Items")
    for item in st.session_state.items:
        if item["status"] == "Available":
            with st.container():
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{item['name']}**")
                col1.caption(f"Lender: {item['owner']} | Rate: ₹{item['price']}/hr")
                if col2.button(f"Request", key=f"req_{item['id']}"):
                    st.session_state.active_rental = {
                        "item": item['name'],
                        "rate": item['price'],
                        "start_time": datetime.now(),
                        "owner": item['owner']
                    }
                    item["status"] = "Busy"
                    st.rerun()
                st.divider()

# --- TAB 2: LEND ---
with tab2:
    st.write("### Post Your Item")
    with st.form("lend_form"):
        i_name = st.text_input("What are you lending?")
        i_price = st.number_input("Rate per Hour (₹)", min_value=1, value=10)
        submitted = st.form_submit_button("List Item Live")
        if submitted:
            new_id = len(st.session_state.items) + 1
            st.session_state.items.append({
                "id": new_id, "name": i_name, "owner": "You", "price": i_price, "status": "Available"
            })
            st.success(f"{i_name} is now visible to others!")

# --- TAB 3: RENTAL STATUS (THE TIMER & CASH LOGIC) ---
with tab3:
    if st.session_state.active_rental:
        rental = st.session_state.active_rental
        st.info(f"Currently Borrowing: **{rental['item']}**")
        
        # Live Calculation
        elapsed = datetime.now() - rental['start_time']
        seconds = elapsed.total_seconds()
        # Minimum 1 hour logic: if less than 3600s, charge full hour
        cost = rental['rate'] if seconds < 3600 else (seconds/3600) * rental['rate']
        
        m1, m2 = st.columns(2)
        m1.metric("Time Elapsed", f"{int(seconds // 60)} mins")
        m2.metric("Total Cost", f"₹{round(cost, 2)}")
        
        st.divider()
        pay_method = st.segmented_control("Payment Method", ["Cash", "In-App Wallet"], default="Cash")
        
        if st.button("Finish & Return Item"):
            if pay_method == "Cash":
                st.warning(f"Hand over ₹{round(cost, 2)} to {rental['owner']}.")
                if st.button("Lender Confirmed Receipt"):
                    st.session_state.active_rental = None
                    # Reset item status to Available
                    for it in st.session_state.items:
                        if it["name"] == rental["item"]: it["status"] = "Available"
                    st.success("Transaction Complete!")
                    st.rerun()
            else:
                st.success("Wallet Payment Successful!")
                st.session_state.active_rental = None
                for it in st.session_state.items:
                    if it["name"] == rental["item"]: it["status"] = "Available"
                st.rerun()
    else:
        st.write("No active transactions.")
        st.image("https://cdn-icons-png.flaticon.com/512/4076/4076432.png", width=100)
