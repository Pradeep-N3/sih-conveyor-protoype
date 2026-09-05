import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# For reproducible results
np.random.seed(42)
random.seed(42)

data = []

# Number of sensor readings to generate
num_samples = 3000

# Starting time
start_time = datetime.now()

# Available conveyor belt splices
splice_ids = [
    "SPLICE_001",
    "SPLICE_002",
    "SPLICE_003",
    "SPLICE_004",
    "SPLICE_005"
]

for i in range(num_samples):

    # Generate timestamp (every 2 seconds)
    timestamp = start_time + timedelta(seconds=i * 2)

    # Select splice
    splice_id = random.choice(splice_ids)

    # Select operating condition
    condition = random.choices(
        ["NORMAL", "WARNING", "CRITICAL"],
        weights=[70, 20, 10]
    )[0]

    # ---------------- NORMAL ----------------
    if condition == "NORMAL":

        surface_distance = np.random.normal(100, 2)
        acoustic_level = np.random.normal(30, 5)
        edge_deviation = abs(np.random.normal(2, 1))
        belt_speed = np.random.normal(1.5, 0.05)
        carryback_level = np.random.uniform(0.0, 0.2)

    # ---------------- WARNING ----------------
    elif condition == "WARNING":

        surface_distance = np.random.normal(106, 3)
        acoustic_level = np.random.normal(55, 8)
        edge_deviation = abs(np.random.normal(7, 2))
        belt_speed = np.random.normal(1.4, 0.1)
        carryback_level = np.random.uniform(0.2, 0.6)

    # ---------------- CRITICAL ----------------
    else:

        surface_distance = np.random.normal(115, 5)
        acoustic_level = np.random.normal(85, 10)
        edge_deviation = abs(np.random.normal(15, 4))
        belt_speed = np.random.normal(1.2, 0.15)
        carryback_level = np.random.uniform(0.6, 1.0)

    # Store the reading
    data.append([
        timestamp,
        splice_id,
        round(surface_distance, 2),
        round(acoustic_level, 2),
        round(edge_deviation, 2),
        round(belt_speed, 2),
        round(carryback_level, 2),
        condition
    ])


# Create DataFrame
df = pd.DataFrame(
    data,
    columns=[
        "timestamp",
        "splice_id",
        "surface_distance",
        "acoustic_level",
        "edge_deviation",
        "belt_speed",
        "carryback_level",
        "condition"
    ]
)

# Save dataset
os.makedirs("data",exist_ok=True)
df.to_csv("data/sensor_dataset.csv", index=False)

print("Dataset generated successfully!")
print(f"Total samples: {len(df)}")

print("\nCondition Distribution:")
print(df["condition"].value_counts())

print("\nFirst 5 rows:")
print(df.head())