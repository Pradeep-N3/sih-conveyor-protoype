import os
import random
from datetime import datetime
import joblib
import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Conveyor Belt Health Monitoring",
    page_icon="⚙️",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
.main-title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: white;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 16px;
    margin-bottom: 20px;
}
.card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #263548;
}
.metric-card {
    background-color: #111827;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263548;
    text-align: center;
}
.sensor-title {
    color: #94a3b8;
    font-size: 14px;
}
.sensor-value {
    color: white;
    font-size: 24px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD ML MODEL & ENCODERS
# ============================================================

@st.cache_resource
def load_ml_artifacts():
    try:
        model = joblib.load("conveyor_model.pkl")
        splice_encoder = joblib.load("splice_encoder.pkl")
        condition_encoder = joblib.load("condition_encoder.pkl")
        return model, splice_encoder, condition_encoder, None
    except Exception as e:
        return None, None, None, str(e)


model, splice_encoder, condition_encoder, model_error = load_ml_artifacts()


# ============================================================
# GENERATE SIMULATED SENSOR DATA
# ============================================================

def generate_sensor_data():
    splice_ids = ["SPLICE_001", "SPLICE_002", "SPLICE_003", "SPLICE_004", "SPLICE_005"]
    simulated_condition = random.choices(["NORMAL", "WARNING", "CRITICAL"], weights=[70, 20, 10])[0]

    if simulated_condition == "NORMAL":
        surface_distance = random.uniform(97, 103)
        acoustic_level = random.uniform(20, 40)
        edge_deviation = random.uniform(0, 3)
        belt_speed = random.uniform(1.45, 1.55)
        carryback_level = random.uniform(0, 0.2)
    elif simulated_condition == "WARNING":
        surface_distance = random.uniform(104, 110)
        acoustic_level = random.uniform(45, 70)
        edge_deviation = random.uniform(5, 10)
        belt_speed = random.uniform(1.3, 1.45)
        carryback_level = random.uniform(0.2, 0.6)
    else:
        surface_distance = random.uniform(110, 125)
        acoustic_level = random.uniform(70, 100)
        edge_deviation = random.uniform(12, 22)
        belt_speed = random.uniform(1.0, 1.3)
        carryback_level = random.uniform(0.6, 1.0)

    return {
        "splice_id": random.choice(splice_ids),
        "surface_distance": round(surface_distance, 2),
        "acoustic_level": round(acoustic_level, 2),
        "edge_deviation": round(edge_deviation, 2),
        "belt_speed": round(belt_speed, 2),
        "carryback_level": round(carryback_level, 2),
        "belt_thickness": round(random.uniform(8, 15), 2)
    }


# ============================================================
# MACHINE LEARNING PREDICTION
# ============================================================

def predict_condition(sensor_data):
    if model is None or splice_encoder is None or condition_encoder is None:
        return "MODEL / ENCODER NOT LOADED"

    try:
        # Encode splice_id string to int
        splice_encoded = splice_encoder.transform([sensor_data["splice_id"]])[0]

        # Structure input DataFrame in exact training order
        input_data = pd.DataFrame([{
            "splice_id": splice_encoded,
            "surface_distance": sensor_data["surface_distance"],
            "acoustic_level": sensor_data["acoustic_level"],
            "edge_deviation": sensor_data["edge_deviation"],
            "belt_speed": sensor_data["belt_speed"],
            "carryback_level": sensor_data["carryback_level"]
        }])

        prediction = model.predict(input_data)
        predicted_condition = condition_encoder.inverse_transform(prediction)[0]
        return str(predicted_condition).upper()

    except Exception as e:
        return f"MODEL ERROR: {str(e)}"


# ============================================================
# CALCULATE HEALTH SCORE
# ============================================================

def calculate_health(sensor):
    score = 100

    if sensor["surface_distance"] < 90:
        score -= 15
    elif sensor["surface_distance"] > 115:
        score -= 10

    if sensor["acoustic_level"] > 85:
        score -= 30
    elif sensor["acoustic_level"] > 70:
        score -= 20
    elif sensor["acoustic_level"] > 60:
        score -= 10

    if sensor["edge_deviation"] > 9:
        score -= 30
    elif sensor["edge_deviation"] > 6:
        score -= 20

    if sensor["carryback_level"] > 0.75:
        score -= 20
    elif sensor["carryback_level"] > 0.5:
        score -= 10

    return max(score, 0)

# ============================================================
# BELT THICKNESS MONITORING
# ============================================================

def check_thickness_status(sensor, belt_config):
    current_thickness = sensor["belt_thickness"]
    standard_thickness = belt_config["standard_thickness"]
    minimum_thickness = belt_config["minimum_thickness"]

    if current_thickness < minimum_thickness:
        return {
            "status": "CRITICAL",
            "alarm": True,
            "message": "BELT THICKNESS BELOW MINIMUM LIMIT"
        }
    elif current_thickness < standard_thickness:
        return {
            "status": "WARNING",
            "alarm": False,
            "message": "BELT THICKNESS BELOW STANDARD LEVEL"
        }
    else:
        return {
            "status": "NORMAL",
            "alarm": False,
            "message": "BELT THICKNESS NORMAL"
        }

# ============================================================
# DETERMINE OVERALL STATUS
# ============================================================

def get_overall_status(prediction, health_score):
    if health_score < 40 or prediction == "CRITICAL":
        return "CRITICAL"
    elif health_score < 70 or prediction == "WARNING":
        return "WARNING"
    else:
        return "HEALTHY"


# ============================================================
# SESSION STATE
# ============================================================
# belt configuration
if "belt_config" not in st.session_state:
    st.session_state.belt_config={
        "belt_id":"BELT_001",
        "company":"Default Company",
        "base_splice_value":100.0,
        "standard_thickness":12.0,
        "minimum_thickness":9.6
    }
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = generate_sensor_data()

if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("⚙️ CONVEX")
    st.caption("BELT HEALTH MONITORING SYSTEM")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📡 Live Monitoring",
            "⚙️ Belt Configuration",
            "🤖 AI Prediction",
            "📊 Analytics",
            "📜 History"
        ]
    )

    st.divider()
    st.subheader("System Status")

    if model is not None and splice_encoder is not None and condition_encoder is not None:
        st.success("● ML MODEL & ENCODERS ONLINE")
    else:
        st.error("● ML MODEL OFFLINE")
        st.caption(str(model_error))

    st.success("● SIMULATION ACTIVE")


# ============================================================
# HEADER
# ============================================================

st.markdown("""
    <div class="main-title">CONVEYOR BELT INTELLIGENT HEALTH MONITORING SYSTEM</div>
    <div class="subtitle">Real-Time Monitoring • AI Prediction • Predictive Maintenance</div>
""", unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 Refresh Data"):
        st.session_state.sensor_data = generate_sensor_data()

with col2:
    st.success("🟢 CONVEYOR SYSTEM RUNNING")


# ============================================================
# CURRENT DATA
# ============================================================

sensor = st.session_state.sensor_data
belt_config = st.session_state.belt_config

prediction = predict_condition(sensor)
health_score = calculate_health(sensor)

thickness_result = check_thickness_status(
    sensor,
    belt_config
)

overall_status = get_overall_status(
    prediction,
    health_score
)

current_record = {
    "timestamp": datetime.now().strftime("%H:%M:%S"),
    "splice_id": sensor["splice_id"],
    "surface_distance": sensor["surface_distance"],
    "acoustic_level": sensor["acoustic_level"],
    "edge_deviation": sensor["edge_deviation"],
    "belt_speed": sensor["belt_speed"],
    "carryback_level": sensor["carryback_level"],
    "belt_thickness": sensor["belt_thickness"],
    "prediction": prediction,
    "health_score": health_score
}

if not st.session_state.history or st.session_state.history[-1]["timestamp"] != current_record["timestamp"]:
    st.session_state.history.append(current_record)

if len(st.session_state.history) > 100:
    st.session_state.history.pop(0)


# ============================================================
# PAGE 1: LIVE MONITORING
# ============================================================

if page == "📡 Live Monitoring":
    st.header("📡 Live Conveyor Monitoring")
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Conveyor Live View")
        st.markdown(f"""
        <div class="card" style="height:280px;text-align:center;">
            <h2>⚙️ CONVEYOR BELT VISUALIZATION</h2>
            <div style="margin-top:70px;height:55px;width:85%;margin-left:auto;margin-right:auto;background:#475569;border-radius:30px;position:relative;">
                <div style="position:absolute;left:48%;top:-18px;font-size:35px;">🔴</div>
            </div>
            <h4 style="margin-top:35px;">📍 SENSOR ZONE: {sensor['splice_id']} MONITORING</h4>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.subheader("Splice Health")
        if health_score >= 70:
            color, status = "#22c55e", "HEALTHY"
        elif health_score >= 40:
            color, status = "#facc15", "WARNING"
        else:
            color, status = "#ef4444", "CRITICAL"

        st.markdown(f"""
        <div class="card" style="height:280px;text-align:center;">
            <p style="font-size:18px;">HEALTH SCORE</p>
            <h1 style="font-size:70px;color:{color};margin-top:35px;">{health_score}</h1>
            <h2 style="color:{color};">{status}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Real-Time Sensor Readings")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("📏 Surface Distance", f'{sensor["surface_distance"]} mm')
    with c2:
        st.metric("🔊 Acoustic Level", f'{sensor["acoustic_level"]} dB')
    with c3:
        st.metric("📐 Edge Deviation", f'{sensor["edge_deviation"]} mm')
    with c4:
        st.metric("⚡ Belt Speed", f'{sensor["belt_speed"]} m/s')
    with c5:
        st.metric("🧹 Carryback Level", sensor["carryback_level"])
    with c6:
        st.metric("📏 Belt Thickness", f'{sensor["belt_thickness"]} mm')

    st.divider()

    # ========================================================
    # BELT THICKNESS STATUS
    # ========================================================
    st.subheader("📏 Belt Thickness Monitoring")

    current_thickness = sensor["belt_thickness"]
    standard_thickness = belt_config["standard_thickness"]
    minimum_thickness = belt_config["minimum_thickness"]

    t1, t2, t3 = st.columns(3)

    with t1:
        st.metric(
            "Current Thickness",
            f"{current_thickness} mm"
        )
    with t2:
        st.metric(
            "Standard Thickness",
            f"{standard_thickness} mm"
        )
    with t3:
        st.metric(
            "Minimum Allowed Thickness",
            f"{minimum_thickness:.2f} mm"
        )

    if thickness_result["status"] == "CRITICAL":
        st.error(
            f"🚨 ALARM: {thickness_result['message']}"
        )
    elif thickness_result["status"] == "WARNING":
        st.warning(
            f"⚠ {thickness_result['message']}"
        )
    else:
        st.success(
            f"✓ {thickness_result['message']}"
        )

    st.divider()

    st.subheader("🤖 AI Prediction Result")
    p1, p2 = st.columns(2)

    with p1:
        if prediction == "NORMAL":
            st.success("### 🟢 ML Prediction: NORMAL")
        elif prediction == "WARNING":
            st.warning("### 🟡 ML Prediction: WARNING")
        elif prediction == "CRITICAL":
            st.error("### 🔴 ML Prediction: CRITICAL")
        else:
            st.error(f"### {prediction}")

    with p2:
        st.subheader("Recommended Action")
        if overall_status == "HEALTHY":
            st.success("✓ Conveyor operating normally. Continue monitoring.")
        elif overall_status == "WARNING":
            st.warning("⚠ Abnormal conditions detected. Schedule inspection.")
        else:
            st.error("🚨 Critical condition detected. Immediate inspection recommended.")

# ============================================================
# PAGE 2: BELT CONFIGURATION
# ============================================================

elif page == "⚙️ Belt Configuration":

    st.header("⚙️ Belt Configuration")

    st.write(
        "Configure the baseline values and specifications "
        "for the currently installed conveyor belt."
    )

    st.divider()

    config = st.session_state.belt_config

    belt_id = st.text_input(
        "Belt ID",
        value=config["belt_id"]
    )

    company = st.text_input(
        "Company Name",
        value=config["company"]
    )

    base_splice_value = st.number_input(
        "Base Splice Value (mm)",
        min_value=0.0,
        value=float(config["base_splice_value"])
    )

    standard_thickness = st.number_input(
        "Standard Belt Thickness (mm)",
        min_value=0.0,
        value=float(config["standard_thickness"])
    )

    minimum_percentage = st.slider(
        "Minimum Allowed Thickness (%)",
        min_value=50,
        max_value=100,
        value=80
    )

    minimum_thickness = (
        standard_thickness * minimum_percentage / 100
    )

    st.info(
        f"Minimum Allowed Thickness: {minimum_thickness:.2f} mm"
    )

    if st.button("💾 Save Belt Configuration"):

        st.session_state.belt_config = {
            "belt_id": belt_id,
            "company": company,
            "base_splice_value": base_splice_value,
            "standard_thickness": standard_thickness,
            "minimum_thickness": minimum_thickness
        }

        st.success("Belt configuration saved successfully!")

# ============================================================
# PAGE 3: AI PREDICTION
# ============================================================

elif page == "🤖 AI Prediction":
    st.header("🤖 Machine Learning Prediction Module")

    if model is None or splice_encoder is None or condition_encoder is None:
        st.error("ML Model or Encoders Not Loaded")
        st.code(model_error)
    else:
        st.success("ML Model and Encoders Loaded Successfully")
        st.divider()
        st.subheader("Current Sensor Input")
        st.dataframe(pd.DataFrame([sensor]), use_container_width=True)
        st.divider()
        st.subheader("Prediction Output")

        if prediction == "NORMAL":
            st.success(f"### 🟢 {prediction}")
        elif prediction == "WARNING":
            st.warning(f"### 🟡 {prediction}")
        elif prediction == "CRITICAL":
            st.error(f"### 🔴 {prediction}")
        else:
            st.error(prediction)


# ============================================================
# PAGE 4: ANALYTICS
# ============================================================

elif page == "📊 Analytics":
    st.header("📊 Conveyor Analytics")
    history_df = pd.DataFrame(st.session_state.history)

    if len(history_df) > 1:
        st.subheader("Health Score Trend")
        st.line_chart(history_df.set_index("timestamp")["health_score"])

        st.subheader("Acoustic Level Trend")
        st.line_chart(history_df.set_index("timestamp")["acoustic_level"])

        st.subheader("Edge Deviation Trend")
        st.line_chart(history_df.set_index("timestamp")["edge_deviation"])
    else:
        st.info("Refresh sensor data multiple times to generate analytics.")


# ============================================================
# PAGE 5: HISTORY
# ============================================================

elif page == "📜 History":
    st.header("📜 Monitoring History")
    history_df = pd.DataFrame(st.session_state.history)

    if not history_df.empty:
        st.dataframe(history_df.iloc[::-1], use_container_width=True)
        csv_data = history_df.to_csv(index=False)
        st.download_button("⬇ Download History CSV", csv_data, "conveyor_history.csv", "text/csv")
    else:
        st.info("No history available.")

st.divider()
st.caption("Conveyor Belt Intelligent Health Monitoring System | SIH Prototype | AI-Based Predictive Maintenance")