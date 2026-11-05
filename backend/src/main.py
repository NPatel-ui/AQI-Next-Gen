
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
STAGING_FILE = ROOT / "data" / "staging" / "all_cities_api_daily_staging.csv"



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



# LOAD AND COMBINE HISTORICAL + LATEST API DATA


try:
    historical_data = pd.read_csv(
        DATA_FILE,
        parse_dates=["date"]
    )

    historical_data["city"] = (
        historical_data["city"].astype(str).str.strip()
    )

    # Keep a copy of the historical dataset's city metadata.
    metadata_columns = [
        column for column in [
            "state", "region", "latitude", "longitude", "elevation_m"
        ]
        if column in historical_data.columns
    ]

    # Keep a separate historical-only copy for historical analytics.
    # API staging records may include forecast-estimated future values and must
    # not be mixed into historical trend charts.
    historical_analytics_data = historical_data.copy()

    # Load the latest API-generated records if the staging file exists.
    if STAGING_FILE.exists():
        api_data = pd.read_csv(
            STAGING_FILE,
            parse_dates=["date"]
        )

        api_data["city"] = api_data["city"].astype(str).str.strip()

        # Add city metadata to API rows from the historical dataset.
        metadata_lookup = (
            historical_data[["city"] + metadata_columns]
            .dropna(subset=["city"])
            .drop_duplicates(subset=["city"], keep="first")
        )
        metadata_lookup["_city_key"] = metadata_lookup["city"].str.lower()

        api_data["_city_key"] = api_data["city"].str.lower()
        api_data = api_data.merge(
            metadata_lookup.drop(columns=["city"]),
            on="_city_key",
            how="left",
            suffixes=("", "_historical")
        )
        api_data.drop(columns=["_city_key"], inplace=True)

        # Preserve historical records on overlapping dates.
        latest_historical_date = historical_data["date"].max()
        api_data = api_data[
            api_data["date"] > latest_historical_date
        ].copy()

        historical_data = pd.concat(
            [historical_data, api_data],
            ignore_index=True,
            sort=False
        )

    historical_data = historical_data.sort_values(
        ["city", "date"]
    ).reset_index(drop=True)

    if historical_data.duplicated(["city", "date"]).any():
        raise ValueError(
            "Duplicate city-date records found after combining datasets."
        )

except Exception as error:
    raise RuntimeError(
        f"Could not load and combine AQI datasets: {error}"
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
        "data_source": "merged_daily.csv + all_cities_api_daily_staging.csv",
        "results": results,
    }




# HISTORICAL ANALYTICS


ANALYTICS_POLLUTANTS = {
    "pm2_5_mean": {"label": "PM2.5", "unit": "µg/m³"},
    "pm10_mean": {"label": "PM10", "unit": "µg/m³"},
    "no2_mean": {"label": "NO₂", "unit": "µg/m³"},
    "so2_mean": {"label": "SO₂", "unit": "µg/m³"},
    "o3_8h_max": {"label": "O₃ (8-hour max)", "unit": "µg/m³"},
    "co_8h_max": {"label": "CO (8-hour max)", "unit": "µg/m³"},
}

ANALYTICS_WEATHER = [
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
    "precipitation_sum",
]


def _analytics_filter(
    city: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    data = historical_analytics_data.copy()

    if city and city.lower() != "all":
        matches = data["city"].str.lower() == city.strip().lower()
        if not matches.any():
            raise HTTPException(status_code=404, detail=f"City '{city}' was not found.")
        data = data[matches]

    if start_date:
        data = data[data["date"].dt.date >= start_date]

    if end_date:
        data = data[data["date"].dt.date <= end_date]

    return data


def _json_records(frame: pd.DataFrame):
    clean = frame.replace({np.nan: None, np.inf: None, -np.inf: None})
    return clean.to_dict(orient="records")


@app.get("/api/analytics/summary")
def analytics_summary():
    data = historical_analytics_data
    return {
        "status": "success",
        "source": "merged_daily.csv (historical records only)",
        "records": int(len(data)),
        "cities": int(data["city"].nunique()),
        "start_date": data["date"].min().date().isoformat(),
        "end_date": data["date"].max().date().isoformat(),
        "pollutants": list(ANALYTICS_POLLUTANTS.keys()),
        "daily_variables": int(len(ANALYTICS_POLLUTANTS) + len(ANALYTICS_WEATHER)),
    }


@app.get("/api/analytics/trends")
def analytics_trends(
    city: str = "All",
    metric: str = "india_aqi",
    start_date: date | None = None,
    end_date: date | None = None,
    group_by: str = "monthly",
):
    if metric not in ["india_aqi", "india_aqi_pm"]:
        raise HTTPException(status_code=422, detail="metric must be india_aqi or india_aqi_pm.")
    if group_by not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=422, detail="group_by must be daily, weekly or monthly.")

    data = _analytics_filter(city, start_date, end_date)
    data = data.dropna(subset=[metric]).copy()

    if city.lower() == "all":
        grouped = data.groupby("date", as_index=False)[metric].mean()
    else:
        grouped = data.groupby("date", as_index=False)[metric].mean()

    grouped = grouped.set_index("date")
    if group_by == "weekly":
        grouped = grouped.resample("W").mean()
    elif group_by == "monthly":
        grouped = grouped.resample("MS").mean()

    grouped = grouped.dropna().reset_index()
    grouped["date"] = grouped["date"].dt.strftime("%Y-%m-%d")
    grouped.rename(columns={metric: "value"}, inplace=True)

    return {
        "status": "success",
        "city": city,
        "metric": metric,
        "group_by": group_by,
        "count": int(len(grouped)),
        "overall_average": round(float(data[metric].mean()), 2) if len(data) else None,
        "data": _json_records(grouped.round({"value": 2})),
    }


@app.get("/api/analytics/cities")
def analytics_cities(
    metric: str = "india_aqi",
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 50,
):
    if metric not in ["india_aqi", "india_aqi_pm"]:
        raise HTTPException(status_code=422, detail="metric must be india_aqi or india_aqi_pm.")
    data = _analytics_filter(None, start_date, end_date)
    grouped = (
        data.groupby("city")[metric]
        .agg(["mean", "max", "count"])
        .reset_index()
        .rename(columns={"mean": "average", "max": "maximum", "count": "records"})
        .sort_values("average", ascending=False)
        .head(max(1, min(limit, 50)))
    )
    grouped[["average", "maximum"]] = grouped[["average", "maximum"]].round(2)
    return {
        "status": "success",
        "metric": metric,
        "data": _json_records(grouped),
    }


@app.get("/api/analytics/categories")
def analytics_categories(
    metric: str = "india_aqi",
    city: str = "All",
    start_date: date | None = None,
    end_date: date | None = None,
):
    category_column = "india_aqi_category" if metric == "india_aqi" else "india_aqi_pm_category" if metric == "india_aqi_pm" else None
    if not category_column:
        raise HTTPException(status_code=422, detail="metric must be india_aqi or india_aqi_pm.")
    data = _analytics_filter(city, start_date, end_date)
    if category_column not in data.columns:
        raise HTTPException(status_code=500, detail=f"Historical data is missing {category_column}.")
    counts = (
        data[category_column].dropna().astype(str).value_counts()
        .rename_axis("category").reset_index(name="records")
    )
    total = int(counts["records"].sum())
    counts["percentage"] = (counts["records"] / total * 100).round(2) if total else 0
    return {
        "status": "success",
        "metric": metric,
        "total": total,
        "data": _json_records(counts),
    }


@app.get("/api/analytics/pollutants")
def analytics_pollutants(
    pollutant: str = "pm2_5_mean",
    city: str = "All",
    start_date: date | None = None,
    end_date: date | None = None,
    group_by: str = "monthly",
):
    if pollutant not in ANALYTICS_POLLUTANTS:
        raise HTTPException(status_code=422, detail=f"Unsupported pollutant. Choose from: {', '.join(ANALYTICS_POLLUTANTS)}")
    if group_by not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=422, detail="group_by must be daily, weekly or monthly.")

    data = _analytics_filter(city, start_date, end_date).dropna(subset=[pollutant]).copy()
    grouped = data.groupby("date")[pollutant].mean().to_frame()
    grouped = grouped.resample({"daily": "D", "weekly": "W", "monthly": "MS"}[group_by]).mean()
    grouped = grouped.dropna().reset_index().rename(columns={pollutant: "value"})
    grouped["date"] = grouped["date"].dt.strftime("%Y-%m-%d")
    grouped["value"] = grouped["value"].round(3)

    return {
        "status": "success",
        "pollutant": pollutant,
        "label": ANALYTICS_POLLUTANTS[pollutant]["label"],
        "unit": ANALYTICS_POLLUTANTS[pollutant]["unit"],
        "city": city,
        "group_by": group_by,
        "data": _json_records(grouped),
    }


@app.get("/api/analytics/seasonal")
def analytics_seasonal(
    metric: str = "india_aqi",
    city: str = "All",
    start_date: date | None = None,
    end_date: date | None = None,
):
    if metric not in ["india_aqi", "india_aqi_pm"]:
        raise HTTPException(status_code=422, detail="metric must be india_aqi or india_aqi_pm.")
    data = _analytics_filter(city, start_date, end_date).dropna(subset=[metric]).copy()
    data["month"] = data["date"].dt.month
    monthly = data.groupby("month")[metric].mean().reindex(range(1, 13)).rename("average").reset_index()
    monthly["average"] = monthly["average"].round(2)
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly["month_name"] = monthly["month"].map(dict(enumerate(month_labels, 1)))

    def season(month):
        if month in [12, 1, 2]:
            return "Winter"
        if month in [3, 4, 5]:
            return "Summer"
        if month in [6, 7, 8, 9]:
            return "Monsoon"
        return "Post-monsoon"

    data["season"] = data["date"].dt.month.map(season)
    seasonal = (
        data.groupby("season")[metric].mean()
        .reindex(["Winter", "Summer", "Monsoon", "Post-monsoon"])
        .rename("average").reset_index()
    )
    seasonal["average"] = seasonal["average"].round(2)

    return {
        "status": "success",
        "metric": metric,
        "monthly": _json_records(monthly),
        "seasonal": _json_records(seasonal),
    }


@app.get("/api/analytics/weather")
def analytics_weather(
    city: str = "All",
    start_date: date | None = None,
    end_date: date | None = None,
    metric: str = "india_aqi",
):
    if metric not in ["india_aqi", "india_aqi_pm"]:
        raise HTTPException(status_code=422, detail="metric must be india_aqi or india_aqi_pm.")
    data = _analytics_filter(city, start_date, end_date).copy()
    available_weather = [column for column in ANALYTICS_WEATHER if column in data.columns]
    correlation_rows = []
    for column in available_weather:
        pair = data[[column, metric]].dropna()
        correlation = pair[column].corr(pair[metric]) if len(pair) >= 2 else np.nan
        correlation_rows.append({
            "weather_variable": column,
            "label": {
                "temperature_2m_mean": "Mean temperature (°C)",
                "relative_humidity_2m_mean": "Relative humidity (%)",
                "wind_speed_10m_max": "Maximum wind speed (km/h)",
                "precipitation_sum": "Precipitation (mm)",
            }.get(column, column),
            "correlation": round(float(correlation), 3) if pd.notna(correlation) else None,
            "records": int(len(pair)),
        })

    scatter_column = "relative_humidity_2m_mean"
    scatter = data[[scatter_column, metric]].dropna()
    if len(scatter) > 800:
        scatter = scatter.sample(n=800, random_state=42)
    scatter = scatter.rename(columns={scatter_column: "weather_value", metric: "aqi"})
    scatter["weather_value"] = scatter["weather_value"].round(2)
    scatter["aqi"] = scatter["aqi"].round(2)

    return {
        "status": "success",
        "metric": metric,
        "scatter_variable": "relative_humidity_2m_mean",
        "scatter_label": "Relative humidity (%)",
        "correlations": correlation_rows,
        "scatter": _json_records(scatter),
    }

