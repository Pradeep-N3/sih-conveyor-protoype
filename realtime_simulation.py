import random
import time
from datetime import datetime

import pandas as pd
import joblib

from decision_engine import (
    calculate_health_score,
    get_risk_level,
    get_recommended_action,
    get_recommended_speed
)


# -----------------------------------
# Load ML Model and Encoders
# -----------------------------------

model = joblib.load("conveyor_model.pkl")

splice_encoder = joblib.load("splice_encoder.pkl")

condition_encoder = joblib.load("condition_encoder.pkl")


print("ML Model loaded successfully!")
print("Starting real-time conveyor monitoring...\n")


# -----------------------------------
# Generate Simulated Sensor Reading
# -----------------------------------

def generate_sensor_reading():

    splice_id = random.choice([
        "SPLICE_001",
        "SPLICE_002",
        "SPLICE_003",
        "SPLICE_004",
        "SPLICE_005"
    ])


    # Randomly simulate operating condition
    simulated_condition = random.choices(
        ["NORMAL", "WARNING", "CRITICAL"],
        weights=[70, 20, 10]
    )[0]


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
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "splice_id": splice_id,
        "surface_distance": round(surface_distance, 2),
        "acoustic_level": round(acoustic_level, 2),
        "edge_deviation": round(edge_deviation, 2),
        "belt_speed": round(belt_speed, 2),
        "carryback_level": round(carryback_level, 2)
    }


# -----------------------------------
# ML Prediction
# -----------------------------------

def predict_condition(sensor_data):

    splice_encoded = splice_encoder.transform(
        [sensor_data["splice_id"]]
    )[0]


    input_data = pd.DataFrame([{
        "splice_id": splice_encoded,
        "surface_distance": sensor_data["surface_distance"],
        "acoustic_level": sensor_data["acoustic_level"],
        "edge_deviation": sensor_data["edge_deviation"],
        "belt_speed": sensor_data["belt_speed"],
        "carryback_level": sensor_data["carryback_level"]
    }])


    prediction = model.predict(input_data)

    predicted_condition = condition_encoder.inverse_transform(
        prediction
    )[0]

    return predicted_condition


# -----------------------------------
# Complete Monitoring Cycle
# -----------------------------------

def run_monitoring_cycle():

    # Generate sensor data
    sensor_data = generate_sensor_reading()


    # ML Prediction
    predicted_condition = predict_condition(sensor_data)


    # Calculate Health Score
    health_score = calculate_health_score(
        sensor_data["surface_distance"],
        sensor_data["acoustic_level"],
        sensor_data["edge_deviation"],
        sensor_data["belt_speed"],
        sensor_data["carryback_level"]
    )


    # Risk Level
    risk_level = get_risk_level(health_score)


    # Recommended Actions
    actions = get_recommended_action(
        health_score,
        sensor_data["acoustic_level"],
        sensor_data["edge_deviation"],
        sensor_data["carryback_level"]
    )


    # Recommended Speed
    recommended_speed = get_recommended_speed(
        health_score,
        sensor_data["belt_speed"]
    )


    # Combine everything
    result = {
        **sensor_data,
        "ml_prediction": predicted_condition,
        "health_score": health_score,
        "risk_level": risk_level,
        "recommended_speed": recommended_speed,
        "recommended_actions": actions
    }


    return result


# -----------------------------------
# Run Real-Time Simulation
# -----------------------------------

if __name__ == "__main__":

    while True:

        result = run_monitoring_cycle()

        print("=" * 50)

        print("CONVEYOR BELT LIVE MONITORING")

        print("=" * 50)

        print("Time:", result["timestamp"])
        print("Splice ID:", result["splice_id"])

        print("\n--- SENSOR DATA ---")

        print("Surface Distance:", result["surface_distance"])
        print("Acoustic Level:", result["acoustic_level"])
        print("Edge Deviation:", result["edge_deviation"])
        print("Belt Speed:", result["belt_speed"])
        print("Carryback Level:", result["carryback_level"])

        print("\n--- AI ANALYSIS ---")

        print("ML Prediction:", result["ml_prediction"])
        print("Health Score:", result["health_score"])
        print("Risk Level:", result["risk_level"])
        print("Recommended Speed:", result["recommended_speed"])

        print("\n--- RECOMMENDED ACTIONS ---")

        for action in result["recommended_actions"]:
            print("-", action)

        print("\n")

        # Generate new reading every 3 seconds
        time.sleep(3)