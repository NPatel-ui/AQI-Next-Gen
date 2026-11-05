
from pathlib import Path
from datetime import timedelta
import json
import urllib.request

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "processed" / "merged_daily.csv"

MODEL_FILE = (
    ROOT / "models" / "initial_models" /
    "india_aqi_best_model.joblib"
)

API_URL = "http://127.0.0.1:8000/api/forecast"

CITY = "Nagpur"
FORECAST_DATE = pd.Timestamp("2026-11-04")


POLLUTION_COLUMNS = [
    "india_aqi",
    "india_aqi_pm",
    "pm2_5_mean",
    "pm2_5_max",
    "pm10_mean",
    "pm10_max",
    "no2_mean",
    "so2_mean",
    "o3_8h_max",
    "co_8h_max",
    "dust_mean",
    "aod_mean",
]



# LOAD REAL HISTORICAL DATA


print("\n======================================")
print(" AQI NEXT-GEN REAL DATA FORECAST TEST")
print("======================================")

df = pd.read_csv(
    DATA_FILE,
    parse_dates=["date"]
)

city_df = (
    df[df["city"] == CITY]
    .sort_values("date")
    .reset_index(drop=True)
)

issue_date = FORECAST_DATE - pd.Timedelta(days=1)

history = city_df[
    city_df["date"] <= issue_date
].tail(8).copy()

if len(history) != 8:
    raise ValueError(
        f"Expected 8 days of history, found {len(history)}"
    )

expected_dates = pd.date_range(
    end=issue_date,
    periods=8,
    freq="D"
)

if not history["date"].reset_index(drop=True).equals(
    pd.Series(expected_dates, name="date")
):
    raise ValueError("Historical dates are not continuous.")

if history["date"].iloc[-1] != issue_date:
    raise ValueError("Latest input date does not match issue date.")

print(f"\nCity: {CITY}")
print(f"Forecast date: {FORECAST_DATE.date()}")
print(f"Latest input date: {issue_date.date()}")
print("\nUsing these real historical dates:")
print(history["date"].dt.strftime("%Y-%m-%d").to_list())



# FEATURE ENGINEERING
# Same logic as feature_engineering.py


features = history.copy()

for column in POLLUTION_COLUMNS:

    for lag in [1, 3, 7]:

        features[f"{column}_lag_{lag}"] = (
            history[column].shift(lag)
        )

for column in POLLUTION_COLUMNS:

    for window in [3, 7]:

        features[f"{column}_rolling_mean_{window}"] = (
            history[column].rolling(
                window=window,
                min_periods=window
            ).mean()
        )

        features[f"{column}_rolling_std_{window}"] = (
            history[column].rolling(
                window=window,
                min_periods=window
            ).std()
        )


# Calendar features are based on the issue date.
features["month"] = history["date"].dt.month
features["day_of_week"] = history["date"].dt.dayofweek
features["day_of_year"] = history["date"].dt.dayofyear

features["month_sin"] = np.sin(
    2 * np.pi * features["month"] / 12
)

features["month_cos"] = np.cos(
    2 * np.pi * features["month"] / 12
)

features["day_of_year_sin"] = np.sin(
    2 * np.pi * features["day_of_year"] / 365.25
)

features["day_of_year_cos"] = np.cos(
    2 * np.pi * features["day_of_year"] / 365.25
)


# Latest row represents the issue date.
row = features.iloc[-1].to_dict()

# Load exact expected feature names.
model = joblib.load(MODEL_FILE)

model_features = list(model.feature_names_in_)

# Select and order exactly as the model expects.
missing = [
    name for name in model_features
    if name not in row
]

if missing:
    raise ValueError(f"Missing features: {missing}")

model_input = {
    name: row[name]
    for name in model_features
}

if len(model_input) != 118:
    raise ValueError(
        f"Expected 118 features, got {len(model_input)}"
    )

if not all(
    np.isfinite(value)
    for value in model_input.values()
    if isinstance(value, (int, float, np.number))
):
    raise ValueError("Non-finite numeric feature detected.")

print("\nFeature preparation successful.")
print("Total model features:", len(model_input))



# SEND REAL FEATURES TO FASTAPI


payload = {
    "model": "both",
    "features": model_input
}

request = urllib.request.Request(
    API_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request, timeout=30) as response:

    result = json.loads(
        response.read().decode("utf-8")
    )



# DISPLAY RESULTS


if result.get("status") != "success":
    raise RuntimeError(f"API error: {result}")

full = result["results"]["full_aqi"]
pm = result["results"]["pm_aqi"]

print("\n======================================")
print(" REAL DATA FORECAST RESULTS")
print("======================================")

print("City:", CITY)
print("Forecast date:", FORECAST_DATE.date())

print("\nFull AQI Model")
print("Raw prediction:", full["raw_prediction"])
print("Final prediction:", full["predicted_aqi"])
print("Was clipped:", full["was_clipped"])

print("\nPM AQI Model")
print("Raw prediction:", pm["raw_prediction"])
print("Final prediction:", pm["predicted_aqi"])
print("Was clipped:", pm["was_clipped"])

print("\n======================================")
print(" REAL DATA API TEST SUCCESSFUL")
print("======================================")
