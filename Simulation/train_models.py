import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.calibration import CalibratedClassifierCV
import joblib
import numpy as np

# ===========================================================
# LOAD DATA
# ===========================================================
# Get folder where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build correct CSV path
CSV_PATH = os.path.join(BASE_DIR, "road_accident_dataset.csv")

# Load dataset
df = pd.read_csv(CSV_PATH)
# ===========================================================
# UTILITY: AUTOMATIC ENCODING
# ===========================================================
def encode_dataframe(df):
    df = df.copy()
    le_dict = {}

    for col in df.select_dtypes(include=["object"]).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le

    return df, le_dict


# ===========================================================
# 1. DRIVER MODEL (Accident Severity)
# ===========================================================
def train_driver(df):
    features = [
        "Weather Conditions",
        "Time of Day",
        "Road Type",
        "Traffic Volume",
        "Urban/Rural",
        "Vehicle Condition",
        "Driver Age Group",
        "Visibility Level"
    ]
    target = "Accident Severity"

    data = df[features + [target]].dropna()
    data_encoded, encoders = encode_dataframe(data)

    X = data_encoded[features]
    y = data_encoded[target]

    # split: train / temp (we'll use temp for a small calibration set)
    X_train_full, X_temp, y_train_full, y_temp = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    # from training set, make a smaller train and calibration split
    X_tr, X_cal, y_tr, y_cal = train_test_split(X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full)

    # train base RF on X_tr
    base_model = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42)
    base_model.fit(X_tr, y_tr)

    # calibrate using a held-out calibration set
    calibrated = CalibratedClassifierCV(estimator=base_model, method='isotonic', cv='prefit')
    calibrated.fit(X_cal, y_cal)

    # save the calibrated classifier (has predict_proba)
    joblib.dump(calibrated, "driver_model.pkl")
    joblib.dump(encoders, "driver_encoders.pkl")
    joblib.dump(features, "driver_features.pkl")

    print("Driver model (calibrated) saved.")


# ===========================================================
# 2. GOVERNMENT MODEL (Economic Loss)
# ===========================================================
def train_government(df):
    # USER-INPUT FEATURES
    user_features = [
        "Region", "Country", "Month", "Time of Day",
        "Road Type", "Weather Conditions",
        "Traffic Volume", "Population Density"
    ]

    # INTERNAL FEATURES (kept as averages during prediction)
    internal_features = [
        "Number of Injuries", "Number of Fatalities", "Medical Cost",
        "Insurance Claims", "Number of Vehicles Involved",
        "Pedestrians Involved", "Cyclists Involved"
    ]

    target = "Economic Loss"

    all_features = all_features = user_features + internal_features
    data = df[all_features + [target]].dropna()

    data_encoded, encoders = encode_dataframe(data)

    X = data_encoded[all_features]
    y = data_encoded[target]

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=400, max_depth=16, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "government_model.pkl")
    joblib.dump(encoders, "government_encoders.pkl")
    joblib.dump(all_features, "government_features.pkl")
    print("Government model saved.")


# ===========================================================
# 3. EMERGENCY RESPONDER MODEL (ERT)
# ===========================================================
def train_responder(df):
    target = "Emergency Response Time"  # Assuming target column in dataset

    # -------------------------
    # Features
    # -------------------------
    required_features = [
        "Country",
        "Region",
        "Urban/Rural",
        "Month",
        "Day of Week",
        "Time of Day",
        "Weather Conditions",
        "Road Type"
    ]

    internal_features = [
        "Population Density",
        "Traffic Volume",
        "Road Condition"
    ]

    all_features = required_features + internal_features

    data = df[all_features + [target]].dropna()
    data_encoded, encoders = encode_dataframe(data)

    X = data_encoded[all_features]
    y = data_encoded[target]

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=300, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "responder_model.pkl")
    joblib.dump(encoders, "responder_encoders.pkl")
    joblib.dump(all_features, "responder_features.pkl")
    print("Responder model saved.")


# ===========================================================
# RUN TRAINING
# ===========================================================
#train_driver(df)
#train_government(df)
train_responder(df)

print("All models trained and saved successfully.")
