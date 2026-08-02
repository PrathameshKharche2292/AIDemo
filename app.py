import streamlit as st
import pdfplumber
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
import re

# ---------------------------------
# DATABASE SETUP
# ---------------------------------

conn = sqlite3.connect("appointments.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    slot TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor TEXT,
    specialization TEXT,
    appointment_time TEXT
)
""")

conn.commit()

# Seed sample doctors if table empty
cursor.execute("SELECT COUNT(*) FROM doctors")
count = cursor.fetchone()[0]

if count == 0:
    doctors = [
        ("Dr Sharma", "Cardiologist", "10:30 AM"),
        ("Dr Mehta", "Endocrinologist", "11:00 AM"),
        ("Dr Joshi", "General Physician", "12:00 PM")
    ]

    cursor.executemany(
        "INSERT INTO doctors(name,specialization,slot) VALUES(?,?,?)",
        doctors
    )
    conn.commit()


# ---------------------------------
# PDF EXTRACTION
# ---------------------------------

def extract_pdf_text(uploaded_file):

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# ---------------------------------
# PARSE MEDICAL VALUES
# ---------------------------------

def extract_metric(text, metric):

    pattern = rf"{metric}\s*[:\-]?\s*(\d+\.?\d*)"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return float(match.group(1))

    return None


# ---------------------------------
# AGENT 1 : REPORT ANALYZER
# ---------------------------------

def report_analyzer(text):

    results = {
        "HbA1c": extract_metric(text, "HbA1c"),
        "LDL": extract_metric(text, "LDL"),
        "VitaminD": extract_metric(text, "VitaminD")
    }

    return results


# ---------------------------------
# AGENT 2 : RISK ASSESSOR
# ---------------------------------

def risk_assessment(metrics):

    risks = []

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        risks.append("⚠ Diabetes Risk")

    if metrics["LDL"] and metrics["LDL"] > 160:
        risks.append("⚠ Cardiac Risk")

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        risks.append("⚠ Vitamin D Deficiency")

    return risks


# ---------------------------------
# AGENT 3 : SPECIALIST RECOMMENDER
# ---------------------------------

def specialist_recommendation(metrics):

    specialists = []

    if metrics["LDL"] and metrics["LDL"] > 160:
        specialists.append("Cardiologist")

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        specialists.append("Endocrinologist")

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        specialists.append("General Physician")

    return list(set(specialists))


# ---------------------------------
# AGENT 4 : APPOINTMENT BOOKING
# ---------------------------------

def book_appointment(specialist):

    cursor.execute(
        "SELECT name,specialization,slot FROM doctors WHERE specialization=? LIMIT 1",
        (specialist,)
    )

    doctor = cursor.fetchone()

    if doctor:

        appointment_date = (
            datetime.now() + timedelta(days=2)
        ).strftime("%d-%b-%Y")

        appointment_time = f"{appointment_date} {doctor[2]}"

        cursor.execute(
            """
            INSERT INTO appointments(
                doctor,
                specialization,
                appointment_time
            )
            VALUES(?,?,?)
            """,
            (doctor[0], doctor[1], appointment_time)
        )

        conn.commit()

        return {
            "doctor": doctor[0],
            "specialization": doctor[1],
            "time": appointment_time
        }

    return None


# ---------------------------------
# AGENT 5 : RECOMMENDATIONS
# ---------------------------------

def lifestyle_recommendations(metrics):

    suggestions = []

    if metrics["LDL"] and metrics["LDL"] > 160:
        suggestions.append(
            "Reduce oily food and increase cardio exercise."
        )

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        suggestions.append(
            "Reduce sugar intake and monitor blood glucose."
        )

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        suggestions.append(
            "Increase sunlight exposure and consider supplements."
        )

    if not suggestions:
        suggestions.append(
            "Maintain healthy lifestyle and annual checkups."
        )

    return suggestions


# ---------------------------------
# HEALTH SCORE
# ---------------------------------

def calculate_health_score(metrics):

    score = 100

    if metrics["LDL"] and metrics["LDL"] > 160:
        score -= 15

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        score -= 15

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        score -= 10

    return max(score, 0)


# ---------------------------------
# STREAMLIT UI
# ---------------------------------

st.set_page_config(
    page_title="MediGenie AI",
    layout="wide"
)

st.title("🏥 MediGenie AI")
st.subheader("Healthcare Appointment Orchestrator & Report Analyzer")

uploaded_file = st.file_uploader(
    "Upload Medical Report (PDF)",
    type=["pdf"]
)

if uploaded_file:

    st.success("Report uploaded successfully")

    with st.spinner("Agent 1 : Report Analyzer Running..."):
        report_text = extract_pdf_text(uploaded_file)
        metrics = report_analyzer(report_text)

    st.success("✅ Report Analyzer Completed")

    st.json(metrics)

    with st.spinner("Agent 2 : Risk Assessment Running..."):
        risks = risk_assessment(metrics)

    st.success("✅ Risk Assessment Completed")

    st.write("### Risk Assessment")

    for r in risks:
        st.write(r)

    with st.spinner("Agent 3 : Specialist Recommendation Running..."):
        specialists = specialist_recommendation(metrics)

    st.success("✅ Specialist Agent Completed")

    st.write("### Recommended Specialists")

    for specialist in specialists:
        st.write("✔", specialist)

    if specialists:

        with st.spinner("Agent 4 : Appointment Scheduler Running..."):

            appointment = book_appointment(specialists[0])

        st.success("✅ Appointment Scheduled")

        st.write("### Appointment Details")

        st.info(f"""
Doctor: {appointment['doctor']}

Specialization: {appointment['specialization']}

Time: {appointment['time']}
""")

    with st.spinner("Agent 5 : Lifestyle Advisor Running..."):

        suggestions = lifestyle_recommendations(metrics)

    st.success("✅ Lifestyle Recommendations Generated")

    st.write("### Lifestyle Suggestions")

    for suggestion in suggestions:
        st.write("👉", suggestion)

    score = calculate_health_score(metrics)

    st.write("## Health Score")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Health Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"}
        }
    ))

    st.plotly_chart(fig, use_container_width=True)