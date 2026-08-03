import streamlit as st
import pdfplumber
import requests
import plotly.graph_objects as go
import re

# ======================================
# CONFIG
# ======================================

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"

# ======================================
# PDF TEXT EXTRACTION
# ======================================

def extract_pdf_text(uploaded_file):

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# ======================================
# METRIC EXTRACTION
# ======================================

def extract_metric(text, metric):

    pattern = rf"{metric}\s*[:\-]?\s*(\d+\.?\d*)"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return float(match.group(1))

    return None

# ======================================
# AGENT 1
# REPORT ANALYZER
# ======================================

def analyze_report(text):

    metrics = {

        "HbA1c": extract_metric(text, "HbA1c"),

        "LDL": extract_metric(text, "LDL"),

        "VitaminD": extract_metric(text, "VitaminD")
    }

    return metrics

# ======================================
# AGENT 2
# RISK ANALYSIS
# ======================================

def risk_analysis(metrics):

    risks = []

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        risks.append("Diabetes Risk")

    if metrics["LDL"] and metrics["LDL"] > 160:
        risks.append("Cardiac Risk")

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        risks.append("Vitamin D Deficiency")

    return risks

# ======================================
# AGENT 3
# SPECIALIST RECOMMENDATION
# ======================================

def recommend_specialists(metrics):

    specialists = []

    if metrics["LDL"] and metrics["LDL"] > 160:
        specialists.append("Cardiologist")

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        specialists.append("Endocrinologist")

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        specialists.append("General Physician")

    return list(set(specialists))

# ======================================
# GOOGLE DOCTOR SEARCH
# ======================================

def search_doctors(specialty, location):

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    query = f"{specialty} in {location}"

    params = {
        "query": query,
        "key": GOOGLE_API_KEY
    }

    try:

        response = requests.get(url, params=params)

        data = response.json()

        doctors = []

        if "results" in data:

            for place in data["results"][:5]:

                doctors.append({

                    "name": place.get("name", "N/A"),

                    "address": place.get(
                        "formatted_address",
                        "N/A"
                    ),

                    "rating": place.get(
                        "rating",
                        "N/A"
                    ),

                    "map_url":
                    f"https://www.google.com/maps/search/?api=1&query="
                    f"{place.get('name','')}"
                })

        return doctors

    except Exception as e:

        st.error(str(e))

        return []

# ======================================
# HEALTH SCORE
# ======================================

def calculate_score(metrics):

    score = 100

    if metrics["LDL"] and metrics["LDL"] > 160:
        score -= 15

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:
        score -= 15

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:
        score -= 10

    return max(score, 0)

# ======================================
# RECOMMENDATIONS
# ======================================

def lifestyle_advice(metrics):

    advice = []

    if metrics["LDL"] and metrics["LDL"] > 160:

        advice.append(
            "Reduce oily food and increase cardio exercises."
        )

    if metrics["HbA1c"] and metrics["HbA1c"] > 6.5:

        advice.append(
            "Limit sugar intake and walk at least 30 minutes daily."
        )

    if metrics["VitaminD"] and metrics["VitaminD"] < 20:

        advice.append(
            "Take Vitamin D supplements and increase sunlight exposure."
        )

    if not advice:

        advice.append(
            "Maintain a healthy lifestyle and annual health checkups."
        )

    return advice

# ======================================
# STREAMLIT UI
# ======================================

st.set_page_config(
    page_title="MediGenie AI",
    layout="wide"
)

st.title("🏥 MediGenie AI")
st.subheader(
    "Agentic Healthcare Report Analyzer & Doctor Finder"
)

st.sidebar.header("Search Configuration")

location = st.sidebar.text_input(
    "Location",
    value="Pune"
)

uploaded_file = st.file_uploader(
    "Upload Medical Report PDF",
    type=["pdf"]
)

if uploaded_file:

    # -------------------------------
    # AGENT 1
    # -------------------------------

    with st.spinner(
        "Agent 1 : Report Analyzer Running..."
    ):

        report_text = extract_pdf_text(uploaded_file)

        metrics = analyze_report(report_text)

    st.success("✅ Report Analyzer Complete")

    st.json(metrics)

    # -------------------------------
    # AGENT 2
    # -------------------------------

    with st.spinner(
        "Agent 2 : Health Risk Assessment..."
    ):

        risks = risk_analysis(metrics)

    st.success("✅ Risk Analysis Complete")

    st.subheader("Risk Assessment")

    for risk in risks:
        st.warning(risk)

    # -------------------------------
    # AGENT 3
    # -------------------------------

    with st.spinner(
        "Agent 3 : Specialist Recommendation..."
    ):

        specialists = recommend_specialists(metrics)

    st.success("✅ Specialists Identified")

    st.subheader(
        "Recommended Specialists"
    )

    for specialist in specialists:

        st.info(specialist)

    # -------------------------------
    # AGENT 4
    # -------------------------------

    st.subheader(
        "Live Doctor Search"
    )

    for specialist in specialists:

        st.write(f"Searching for {specialist}")

        doctors = search_doctors(
            specialist,
            location
        )

        for doctor in doctors:

            with st.container():

                st.markdown("---")

                st.write(
                    f"### 👨‍⚕️ {doctor['name']}"
                )

                st.write(
                    f"📍 {doctor['address']}"
                )

                st.write(
                    f"⭐ Rating: {doctor['rating']}"
                )

                st.markdown(
                    f"[View on Google Maps]"
                    f"({doctor['map_url']})"
                )

                if st.button(
                    f"Book Appointment - {doctor['name']}"
                ):
                    st.success(
                        f"""
Appointment Request Submitted

Doctor:
{doctor['name']}

Location:
{doctor['address']}
"""
                    )

    # -------------------------------
    # AGENT 5
    # -------------------------------

    st.subheader(
        "Lifestyle Recommendations"
    )

    advice = lifestyle_advice(metrics)

    for item in advice:
        st.write("✅", item)

    # -------------------------------
    # HEALTH SCORE
    # -------------------------------

    score = calculate_score(metrics)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={
                "text": "Health Score"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "color": "green"
                }
            }
        )
    )

    st.subheader("Health Score")

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------------
    # FOLLOWUP
    # -------------------------------

    st.subheader(
        "Follow-up Plan"
    )

    st.write(
        "📅 Repeat Health Checkup in 3 Months"
    )

    st.write(
        "📅 Consult Recommended Specialist"
    )

    st.write(
        "📅 Track Cholesterol, HbA1c and Vitamin D Levels"
    )