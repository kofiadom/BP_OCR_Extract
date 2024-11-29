import streamlit as st
from database import (
    create_bp_record,
    read_bp_records,
    create_reminder,
    read_reminders,
    delete_reminder,
    list_clinicians,
)
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import base64
import cv2
from ocr import analyze_image

# Streamlit Page Config
st.set_page_config(page_title="CardioMed", layout="wide", page_icon="❤️")

# App Title
st.title("📊CardioMed")
st.subheader("Your BP Companion")

# Sidebar Navigation
menu = st.sidebar.selectbox(
    "Menu", 
    ["Record BP Measurements", "Reminders", "User's History", "Connect with Clinician", "Ask AI Assistant"]
)

# 1. Recording BP Measurements
if menu == "Record BP Measurements":
    st.header("Record Your BP Measurements")

    # Option to use OCR to get BP data from an image
    st.subheader("Option 1: Use OCR to Record BP")
    uploaded_file = st.file_uploader("Upload an image of a blood pressure device", type=["jpg", "jpeg"])

    if uploaded_file is not None: 
        # Encode the uploaded image 
        base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
        analyze_image(base64_image)

    if st.button("Open Camera"):
        ctx = st.camera_input("Take a photo of the blood pressure device")
        
        if ctx:  # Capture the image 
            img_array = ctx.get_image_data() 
            image_bytes = cv2.imencode('.jpg', img_array) 
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            analyze_image(base64_image)

    # Manual BP Input Form
    st.subheader("Option 2: Manual BP Input")
    with st.form("record_bp_form"):
        systolic = st.number_input("Systolic Pressure (e.g., 120)", min_value=50, max_value=250, step=1)
        diastolic = st.number_input("Diastolic Pressure (e.g., 80)", min_value=30, max_value=150, step=1)
        pulse = st.number_input("Pulse (eg: 80): )", min_value=30, max_value=150, step=1)
        measurement_time = datetime.now()
        submitted = st.form_submit_button("Record BP")

        if submitted:
            # Risk Calculation Based on WHO's Formula
            risk_score = 0.5 * systolic + 0.3 * diastolic  # Replace with exact WHO calculation
            create_bp_record(systolic, diastolic, pulse, risk_score, measurement_time)
            st.success(f"BP recorded: {systolic}/{diastolic} | Risk Score: {risk_score:.2f}")

# 2. Reminders
elif menu == "Reminders":
    st.header("Manage Measurement Reminders")
    st.write("Set reminders to record your BP.")

    # Add Reminder
    with st.form("add_reminder_form"):
        reminder_time = st.time_input("Select Time")
        submitted = st.form_submit_button("Add Reminder")
        if submitted:
            reminder_time_str = reminder_time.strftime("%H:%M:%S")
            create_reminder(reminder_time_str)
            st.success(f"Reminder set for {reminder_time_str}.")

    # List and Delete Reminders
    st.subheader("Your Reminders")
    reminders = read_reminders()
    if reminders:
        for reminder in reminders:
            st.write(f"Reminder ID: {reminder['id']} | Time: {reminder['time']}")
            if st.button(f"Delete Reminder {reminder['id']}"):
                delete_reminder(reminder["id"])
                st.experimental_rerun()
    else:
        st.info("No reminders set.")

# 3. User's History
elif menu == "User's History":
    st.header("Your BP History")
    bp_records = read_bp_records()
    if bp_records:
        df = pd.DataFrame(bp_records, columns=["id", "systolic", "diastolic", "pulse", "risk_score", "measurement_time"])
        st.dataframe(df)

        # Visualization
        if st.button("Visualize BP Trends"):
            fig = px.line(
                df, 
                x="measurement_time", 
                y=["systolic", "diastolic"], 
                title="BP Trends Over Time",
                markers=True
            )
            st.plotly_chart(fig)
    else:
        st.info("No BP records found.")

# 4. Connect with Clinician
elif menu == "Connect with Clinician":
    st.header("Connect with a Clinician")
    clinicians = list_clinicians()

    if clinicians:
        for clinician in clinicians:
            st.write(f"**Name:** {clinician['name']}")
            st.write(f"**Specialty:** {clinician['specialty']}")
            st.write(f"**Contact:** {clinician['contact']}")
            if st.button(f"Connect with {clinician['name']}"):
                st.success(f"You've connected with {clinician['name']}.")
    else:
        st.info("No clinicians available.")

# 5. Ask AI Assistant
elif menu == "Ask AI Assistant":
    st.header("Ask AI Assistant")
    st.info("This feature is under development.")
