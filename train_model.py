import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report


# Load dataset
df = pd.read_csv("data/sensor_dataset.csv")

print("Dataset loaded successfully!")
print(f"Total samples: {len(df)}")


# -----------------------------
# Prepare the data
# -----------------------------

# Remove timestamp because it is not useful for initial training
df = df.drop("timestamp", axis=1)


# Encode splice IDs
splice_encoder = LabelEncoder()

df["splice_id"] = splice_encoder.fit_transform(df["splice_id"])


# Encode target condition
condition_encoder = LabelEncoder()

df["condition"] = condition_encoder.fit_transform(df["condition"])


# Features
X = df.drop("condition", axis=1)

# Target
y = df["condition"]


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -----------------------------
# Train Random Forest Model
# -----------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)


# -----------------------------
# Test Model
# -----------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=condition_encoder.classes_
    )
)


# -----------------------------
# Save Model and Encoders
# -----------------------------

joblib.dump(model, "conveyor_model.pkl")

joblib.dump(splice_encoder, "splice_encoder.pkl")

joblib.dump(condition_encoder, "condition_encoder.pkl")


print("\nModel saved successfully!")
print("Files created:")
print("- conveyor_model.pkl")
print("- splice_encoder.pkl")
print("- condition_encoder.pkl")