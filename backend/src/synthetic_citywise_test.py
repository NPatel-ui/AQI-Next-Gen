
from pathlib import Path
from datetime import timedelta
import argparse
import json
import urllib.request
import urllib.error

import joblib
import numpy as np
import pandas as pd



# PROJECT PATHS AND SETTINGS


ROOT = Path(__file__).resolve().parents[1]

CITIES_FILE = ROOT / "data" / "raw" / "cities.csv"

MODEL_FILE = (
    ROOT / "models" / "initial_models" /
    "india_aqi_best_model.joblib"
)

OUTPUT_DIR = ROOT / "data" / "reports" / "functional_testing"

API_URL = "http://127.0.0.1:8000/api/forecast"

RANDOM_SEED = 42

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

WEATHER_COLUMNS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",
    "precipitation_sum",
    "precipitation_hours",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
    "wind_direction_10m_dominant",
    "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
    "weather_code",
]



# GENERATE SYNTHETIC POLLUTION AND WEATHER DATA


def generate_synthetic_history(rng, dates):

    records = []

    for date in dates:

        pm25 = rng.uniform(5, 120)
        pm10 = rng.uniform(10, 250)

        records.append({
            "date": date,

            "india_aqi": rng.uniform(40, 350),
            "india_aqi_pm": rng.uniform(10, 250),

            "pm2_5_mean": pm25,
            "pm2_5_max": pm25 * rng.uniform(1.1, 2.0),

            "pm10_mean": pm10,
            "pm10_max": pm10 * rng.uniform(1.1, 2.0),

            "no2_mean": rng.uniform(2, 80),
            "so2_mean": rng.uniform(1, 50),
            "o3_8h_max": rng.uniform(10, 180),
            "co_8h_max": rng.uniform(100, 2000),

            "dust_mean": rng.uniform(1, 300),
            "aod_mean": rng.uniform(0.05, 1.5),

            "temperature_2m_max": rng.uniform(25, 42),
            "temperature_2m_min": rng.uniform(12, 28),
            "temperature_2m_mean": rng.uniform(20, 35),

            "apparent_temperature_max": rng.uniform(25, 45),
            "precipitation_sum": rng.uniform(0, 20),
            "precipitation_hours": rng.uniform(0, 12),

            "relative_humidity_2m_mean": rng.uniform(20, 95),
            "wind_speed_10m_max": rng.uniform(2, 35),
            "wind_direction_10m_dominant": rng.uniform(0, 360),

            "shortwave_radiation_sum": rng.uniform(5, 30),
            "et0_fao_evapotranspiration": rng.uniform(1, 8),

            "weather_code": int(rng.integers(0, 100)),
        })

    return pd.DataFrame(records)



# PREPARE THE EXACT 118 MODEL FEATURES


def prepare_features(city, forecast_date, model_features, rng):

    # Model predicts the day after the latest input day.
    issue_date = forecast_date - timedelta(days=1)

    # Eight days: seven previous days plus issue date.
    dates = pd.date_range(
        end=issue_date,
        periods=8,
        freq="D"
    )

    df = generate_synthetic_history(rng, dates)

    # Current-day and historical pollution/weather features.
    features = df.copy()

    # Lag features.
    for column in POLLUTION_COLUMNS:

        for lag in [1, 3, 7]:

            features[f"{column}_lag_{lag}"] = (
                df[column].shift(lag)
            )

    # Rolling features, including the current day.
    for column in POLLUTION_COLUMNS:

        for window in [3, 7]:

            features[f"{column}_rolling_mean_{window}"] = (
                df[column].rolling(
                    window=window,
                    min_periods=window
                ).mean()
            )

            features[f"{column}_rolling_std_{window}"] = (
                df[column].rolling(
                    window=window,
                    min_periods=window
                ).std()
            )

    # Calendar features for the forecast issue date.
    features["month"] = df["date"].dt.month
    features["day_of_week"] = df["date"].dt.dayofweek
    features["day_of_year"] = df["date"].dt.dayofyear

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

    # Take the latest day as the prediction input.
    row = features.iloc[-1].to_dict()

    # Add city information.
    row["city"] = city["city"]
    row["latitude"] = city["latitude"]
    row["longitude"] = city["longitude"]

    # Match the saved model's exact feature order.
    missing = [
        name for name in model_features
        if name not in row
    ]

    if missing:
        raise ValueError(
            f"Missing model features: {missing}"
        )

    ordered_features = {
        name: row[name]
        for name in model_features
    }

    if len(ordered_features) != 118:
        raise ValueError(
            f"Expected 118 features, got {len(ordered_features)}"
        )

    return ordered_features, issue_date



# SEND REQUEST TO FASTAPI


def call_api(city_name, forecast_date, features):

    payload = {
        "model": "both",
        "features": features
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=30) as response:

        result = json.loads(response.read().decode("utf-8"))

    if result.get("status") != "success":
        raise RuntimeError(f"API failed: {result}")

    predictions = result["results"]

    return {
        "city": city_name,
        "forecast_date": forecast_date.strftime("%Y-%m-%d"),

        "full_aqi_raw": predictions["full_aqi"]["raw_prediction"],
        "full_aqi": predictions["full_aqi"]["predicted_aqi"],
        "full_aqi_clipped": predictions["full_aqi"]["was_clipped"],

        "pm_aqi_raw": predictions["pm_aqi"]["raw_prediction"],
        "pm_aqi": predictions["pm_aqi"]["predicted_aqi"],
        "pm_aqi_clipped": predictions["pm_aqi"]["was_clipped"],

        "status": "PASS"
    }



# MAIN TEST


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--forecast-date",
        default="2026-11-06",
        help="Date to forecast in YYYY-MM-DD format"
    )

    args = parser.parse_args()

    forecast_date = pd.Timestamp(
        args.forecast_date
    ).date()

    print("\n======================================")
    print(" AQI NEXT-GEN SYNTHETIC CITYWISE TEST")
    print("======================================")

    # Load city metadata only.
    cities = pd.read_csv(CITIES_FILE)

    required_columns = [
        "city",
        "latitude",
        "longitude"
    ]

    if not all(col in cities.columns for col in required_columns):
        raise ValueError("City metadata columns are missing.")

    # Read model feature names.
    model = joblib.load(MODEL_FILE)
    model_features = list(model.feature_names_in_)

    if len(model_features) != 118:
        raise ValueError("The saved model does not expect 118 features.")

    rng = np.random.default_rng(RANDOM_SEED)

    results = []
    failures = []

    print(f"\nForecast date: {forecast_date}")
    print(f"Cities to test: {len(cities)}")
    print("Models: Full AQI + PM AQI")
    print("Input data: Synthetic random values")
    print("Dataset splits: NOT USED\n")

    for index, city in cities.iterrows():

        city_name = city["city"]

        try:

            features, issue_date = prepare_features(
                city,
                forecast_date,
                model_features,
                rng
            )

            result = call_api(
                city_name,
                forecast_date,
                features
            )

            results.append(result)

            print(
                f"[{index + 1:02d}/{len(cities)}] "
                f"{city_name:25s} "
                f"Full AQI: {result['full_aqi']:7.2f} | "
                f"PM AQI: {result['pm_aqi']:7.2f} | PASS"
            )

        except Exception as error:

            failures.append({
                "city": city_name,
                "error": str(error)
            })

            print(
                f"[{index + 1:02d}/{len(cities)}] "
                f"{city_name:25s} FAILED: {error}"
            )

    # Save successful results.
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR /
        "synthetic_citywise_api_test.csv"
    )

    if results:

        result_df = pd.DataFrame(results)

        result_df.to_csv(
            output_file,
            index=False
        )

    # Final summary.
    print("\n======================================")
    print(" TEST SUMMARY")
    print("======================================")

    print(f"Total cities: {len(cities)}")
    print(f"Successful cities: {len(results)}")
    print(f"Failed cities: {len(failures)}")

    print(f"Full AQI predictions: {len(results)}")
    print(f"PM AQI predictions: {len(results)}")

    if results:
        print(f"\nReport saved to:\n{output_file}")

    if failures:

        failure_file = (
            OUTPUT_DIR /
            "synthetic_citywise_failures.csv"
        )

        pd.DataFrame(failures).to_csv(
            failure_file,
            index=False
        )

        print(f"\nFailure report:\n{failure_file}")

    if len(results) == len(cities):
        print("\nALL CITY TESTS PASSED!")
    else:
        print("\nSOME CITY TESTS FAILED. Check the errors above.")


if __name__ == "__main__":
    main()
