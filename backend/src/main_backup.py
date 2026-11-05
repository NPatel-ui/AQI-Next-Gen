
from pathlib import Path
from datetime import date, timedelta
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field



# PATH CONFIGURATION


ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = ROOT / "models" / "initial_models"

FULL_MODEL_PATH = MODEL_DIR / "india_aqi_best_model.joblib"
PM_MODEL_PATH = MODEL_DIR / "india_aqi_pm_best_model.joblib"

DATA_FILE = ROOT / "data" / "processed" / "merged_daily.csv"



# FEATURE CONFIGURATION


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

LAG_PERIODS = [1, 3, 7]
ROLLING_WINDOWS = [3, 7]



# LOAD TRAINED MODELS


try:
    full_aqi_model = joblib.load(FULL_MODEL_PATH)
    pm_aqi_model = joblib.load(PM_MODEL_PATH)

    full_features = list(full_aqi_model.feature_names_in_)
    pm_features = list(pm_aqi_model.feature_names_in_)

except Exception as error:
    raise RuntimeError(
        f"Could not load AQI models: {error}"
    ) from error



# LOAD HISTORICAL DATA


try:
    historical_data = pd.read_csv(
        DATA_FILE,
        parse_dates=["date"]
    )

    historical_data["city"] = (
        historical_data["city"].astype(str).str.strip()
    )

    historical_data = historical_data.sort_values(
        ["city", "date"]
    ).reset_index(drop=True)

except Exception as error:
    raise RuntimeError(
        f"Could not load historical dataset: {error}"
    ) from error


# Check required historical columns.
REQUIRED_COLUMNS = [
    "date",
    "city",
    "latitude",
    "longitude",
] + POLLUTION_COLUMNS + WEATHER_COLUMNS

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in historical_data.columns
]

if missing_columns:
    raise RuntimeError(
        f"Historical dataset is missing columns: {missing_columns}"
    )



# FASTAPI APPLICATION


app = FastAPI(
    title="AQI Next-Gen API",
    description=(
        "AI-powered India-wide AQI forecasting API "
        "using trained HistGradientBoosting models."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# REQUEST SCHEMAS


class ForecastRequest(BaseModel):
    model: Literal["full", "pm", "both"] = "both"

    features: dict[str, Any] = Field(
        ...,
        description="Prepared model features."
    )


class CityDateForecastRequest(BaseModel):
    city: str = Field(
        ...,
        min_length=1,
        description="Indian city name."
    )

    forecast_date: date = Field(
        ...,
        description="Date to forecast in YYYY-MM-DD format."
    )



# MODEL PREDICTION


def validate_features(
    supplied_features: dict[str, Any],
    expected_features: list[str],
):

    missing = [
        feature
        for feature in expected_features
        if feature not in supplied_features
    ]

    extra = [
        feature
        for feature in supplied_features
        if feature not in expected_features
    ]

    if missing:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Required model features are missing.",
                "missing_features": missing,
            },
        )

    if extra:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Unexpected features supplied.",
                "extra_features": extra,
            },
        )

    ordered_features = {
        feature: supplied_features[feature]
        for feature in expected_features
    }

    return pd.DataFrame([ordered_features])


def generate_prediction(model, features):

    try:
        raw_prediction = float(
            model.predict(features)[0]
        )

        if not np.isfinite(raw_prediction):
            raise ValueError(
                "Model returned a non-finite prediction."
            )

        final_prediction = float(
            np.clip(raw_prediction, 0, 500)
        )

        return {
            "raw_prediction": round(raw_prediction, 2),
            "predicted_aqi": round(final_prediction, 2),
            "was_clipped": raw_prediction != final_prediction,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}",
        ) from error


def predict_both_models(features):

    full_input = validate_features(
        features,
        full_features,
    )

    pm_input = validate_features(
        features,
        pm_features,
    )

    return {
        "full_aqi": generate_prediction(
            full_aqi_model,
            full_input,
        ),
        "pm_aqi": generate_prediction(
            pm_aqi_model,
            pm_input,
        ),
    }



# AUTOMATIC FEATURE ENGINEERING


def prepare_city_features(city_name, forecast_date):

    # Model predicts the next day.
    issue_date = forecast_date - timedelta(days=1)

    city_data = historical_data[
        historical_data["city"].str.lower()
        == city_name.lower()
    ].copy()

    if city_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city_name}' was not found."
        )

    # Use only records available on or before the issue date.
    history = city_data[
        city_data["date"].dt.date <= issue_date
    ].tail(8).copy()

    if len(history) != 8:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Insufficient historical data for {city_name}. "
                "Eight consecutive days are required."
            )
        )

    history = history.sort_values("date").reset_index(drop=True)

    expected_dates = pd.date_range(
        end=pd.Timestamp(issue_date),
        periods=8,
        freq="D"
    )

    actual_dates = pd.DatetimeIndex(history["date"])

    if not actual_dates.equals(expected_dates):
        raise HTTPException(
            status_code=422,
            detail=(
                "Historical data has missing dates. "
                "Eight consecutive days are required."
            )
        )

    if history["date"].duplicated().any():
        raise HTTPException(
            status_code=422,
            detail="Duplicate city-date records were found."
        )

    
    # Reproduce original feature engineering
    

    features = history.copy()

    # Pollution lag features.
    for column in POLLUTION_COLUMNS:

        for lag in LAG_PERIODS:

            features[f"{column}_lag_{lag}"] = (
                history[column].shift(lag)
            )

    # Rolling means and standard deviations.
    for column in POLLUTION_COLUMNS:

        for window in ROLLING_WINDOWS:

            features[f"{column}_rolling_mean_{window}"] = (
                history[column]
                .rolling(
                    window=window,
                    min_periods=window
                )
                .mean()
            )

            features[f"{column}_rolling_std_{window}"] = (
                history[column]
                .rolling(
                    window=window,
                    min_periods=window
                )
                .std()
            )

    # Calendar features for the issue date.
    features["month"] = history["date"].dt.month

    features["day_of_week"] = (
        history["date"].dt.dayofweek
    )

    features["day_of_year"] = (
        history["date"].dt.dayofyear
    )

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

    # Latest row represents the forecast issue date.
    latest_row = features.iloc[-1]

    # Use the exact model feature names and order.
    model_input = {}

    for name in full_features:

        if name not in latest_row.index:
            raise HTTPException(
                status_code=500,
                detail=f"Feature engineering did not create: {name}"
            )

        value = latest_row[name]

        if pd.isna(value):
            raise HTTPException(
                status_code=422,
                detail=f"Feature '{name}' contains a missing value."
            )

        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, (int, float)):
            if not np.isfinite(value):
                raise HTTPException(
                    status_code=422,
                    detail=f"Feature '{name}' is not finite."
                )

        model_input[name] = value

    if len(model_input) != 118:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Expected 118 features, "
                f"prepared {len(model_input)}."
            )
        )

    return model_input, history, issue_date



# ROUTES


@app.get("/")
def home():

    return {
        "project": "AQI Next-Gen",
        "message": "AQI forecasting API is running.",
        "version": "2.0.0",
        "documentation": "/docs",
    }


@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "historical_data_loaded": not historical_data.empty,
        "available_cities": int(
            historical_data["city"].nunique()
        ),
        "latest_data_date": (
            historical_data["date"].max().date().isoformat()
        ),
        "models": {
            "full_aqi": {
                "loaded": full_aqi_model is not None,
                "expected_features": len(full_features),
            },
            "pm_aqi": {
                "loaded": pm_aqi_model is not None,
                "expected_features": len(pm_features),
            },
        },
    }



# Get all cities for frontend dropdown


@app.get("/api/cities")
def get_cities():

    cities = sorted(
        historical_data["city"].dropna().unique().tolist()
    )

    return {
        "status": "success",
        "count": len(cities),
        "cities": cities,
    }



# Existing endpoint: pre-prepared features


@app.post("/api/forecast")
def forecast(request: ForecastRequest):

    results = {}

    if request.model in ["full", "both"]:

        full_input = validate_features(
            request.features,
            full_features,
        )

        results["full_aqi"] = generate_prediction(
            full_aqi_model,
            full_input,
        )

    if request.model in ["pm", "both"]:

        pm_input = validate_features(
            request.features,
            pm_features,
        )

        results["pm_aqi"] = generate_prediction(
            pm_aqi_model,
            pm_input,
        )

    return {
        "project": "AQI Next-Gen",
        "status": "success",
        "forecast_type": "model_inference",
        "results": results,
    }



# NEW endpoint: city + date only


@app.post("/api/forecast/by-city-date")
def forecast_by_city_date(
    request: CityDateForecastRequest
):

    city_name = request.city.strip()

    model_input, history, issue_date = prepare_city_features(
        city_name,
        request.forecast_date,
    )

    results = predict_both_models(model_input)

    return {
        "project": "AQI Next-Gen",
        "status": "success",
        "forecast_type": "real_historical_data_inference",
        "city": city_name,
        "forecast_date": request.forecast_date.isoformat(),
        "input_start_date": history["date"].min().date().isoformat(),
        "input_end_date": issue_date.isoformat(),
        "input_days": len(history),
        "features_prepared": len(model_input),
        "data_source": "merged_daily.csv",
        "results": results,
    }
