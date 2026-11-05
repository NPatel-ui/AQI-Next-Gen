from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
import json
import time

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

CITIES_FILE = ROOT / "data" / "raw" / "cities.csv"
AIR_FILE = ROOT / "data" / "raw" / "air_quality_daily.csv"
WEATHER_FILE = ROOT / "data" / "raw" / "weather_daily.csv"

OUTPUT_DIR = ROOT / "data" / "staging"
OUTPUT_FILE = OUTPUT_DIR / "all_cities_api_daily_staging.csv"
ERROR_FILE = OUTPUT_DIR / "daily_update_errors.csv"
VALIDATION_FILE = OUTPUT_DIR / "nagpur_api_validation.csv"

TIMEZONE = "Asia/Kolkata"
VALIDATION_CITY = "Nagpur"
VALIDATION_DATE = "2026-11-03"

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

AQI_BREAKPOINTS = {
    "pm2_5_mean": [
        (0, 30, 0, 50),
        (30, 60, 50, 100),
        (60, 90, 100, 200),
        (90, 120, 200, 300),
        (120, 250, 300, 400),
        (250, 10000, 400, 500),
    ],
    "pm10_mean": [
        (0, 50, 0, 50),
        (50, 100, 50, 100),
        (100, 250, 100, 200),
        (250, 350, 200, 300),
        (350, 430, 300, 400),
        (430, 10000, 400, 500),
    ],
    "no2_mean": [
        (0, 40, 0, 50),
        (40, 80, 50, 100),
        (80, 180, 100, 200),
        (180, 280, 200, 300),
        (280, 400, 300, 400),
        (400, 10000, 400, 500),
    ],
    "so2_mean": [
        (0, 40, 0, 50),
        (40, 80, 50, 100),
        (80, 380, 100, 200),
        (380, 800, 200, 300),
        (800, 1600, 300, 400),
        (1600, 10000, 400, 500),
    ],
    "o3_8h_max": [
        (0, 50, 0, 50),
        (50, 100, 50, 100),
        (100, 168, 100, 200),
        (168, 208, 200, 300),
        (208, 748, 300, 400),
        (748, 10000, 400, 500),
    ],
    "co_8h_max": [
        (0, 1000, 0, 50),
        (1000, 2000, 50, 100),
        (2000, 10000, 100, 200),
        (10000, 17000, 200, 300),
        (17000, 34000, 300, 400),
        (34000, 1000000, 400, 500),
    ],
}

POLLUTANT_LABELS = {
    "pm2_5_mean": "PM2.5",
    "pm10_mean": "PM10",
    "no2_mean": "NO2",
    "so2_mean": "SO2",
    "o3_8h_max": "O3",
    "co_8h_max": "CO",
}


def calculate_sub_index(value, breakpoints):
    if pd.isna(value) or value < 0:
        return None

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= value <= c_high:
            result = (
                (i_high - i_low)
                * (value - c_low)
                / (c_high - c_low)
                + i_low
            )
            return min(500, max(0, round(result)))

    return 500


def classify_aqi(value):
    if pd.isna(value):
        return "Unavailable"
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Satisfactory"
    if value <= 200:
        return "Moderate"
    if value <= 300:
        return "Poor"
    if value <= 400:
        return "Very Poor"
    return "Severe"


def calculate_daily_aqi(row):
    sub_indices = {}

    for pollutant, breakpoints in AQI_BREAKPOINTS.items():
        # Open-Meteo values and the configured breakpoints are both µg/m³.
        value = row[pollutant]
        sub_indices[pollutant] = calculate_sub_index(value, breakpoints)

    available = {
        key: value
        for key, value in sub_indices.items()
        if value is not None
    }

    pm_values = [
        sub_indices["pm2_5_mean"],
        sub_indices["pm10_mean"],
    ]
    pm_values = [value for value in pm_values if value is not None]

    pm_aqi = max(pm_values) if pm_values else None
    full_aqi = max(available.values()) if available else None

    dominant = (
        POLLUTANT_LABELS[max(available, key=available.get)]
        if available
        else "Unavailable"
    )

    return pd.Series({
        "india_aqi": full_aqi,
        "india_aqi_pm": pm_aqi,
        "india_aqi_category": classify_aqi(full_aqi),
        "india_aqi_pm_category": classify_aqi(pm_aqi),
        "dominant_pollutant": dominant,
    })


def fetch_api(url, parameters, retries=3):
    full_url = url + "?" + urlencode(parameters)
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            with urlopen(full_url, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))

            if data.get("error"):
                raise RuntimeError(data.get("reason", "API returned an error"))

            return data

        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt < retries:
                wait_seconds = attempt * 2
                print(f"    API attempt {attempt} failed: {exc}")
                print(f"    Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)

    raise RuntimeError(f"API request failed after {retries} attempts: {last_error}")


def fetch_city_daily(city_row):
    city_name = str(city_row["city"])
    latitude = float(city_row["latitude"])
    longitude = float(city_row["longitude"])

    print(f"\nProcessing {city_name}...")

    # Fetch hourly air-quality values.
    air_data = fetch_api(
        AIR_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": (
                "pm2_5,pm10,nitrogen_dioxide,"
                "sulphur_dioxide,ozone,carbon_monoxide,"
                "dust,aerosol_optical_depth"
            ),
            "timezone": TIMEZONE,
            # Three past days ensure rolling 8-hour windows cross midnight.
            "past_days": 3,
            "forecast_days": 2,
        },
    )

    hourly = air_data["hourly"]

    air_df = pd.DataFrame({
        "time": hourly["time"],
        "pm2_5_mean": hourly["pm2_5"],
        "pm10_mean": hourly["pm10"],
        "no2_mean": hourly["nitrogen_dioxide"],
        "so2_mean": hourly["sulphur_dioxide"],
        "ozone": hourly["ozone"],
        "co": hourly["carbon_monoxide"],
        "dust_mean": hourly["dust"],
        "aod_mean": hourly["aerosol_optical_depth"],
    })

    air_df["time"] = pd.to_datetime(air_df["time"])
    air_df["date"] = air_df["time"].dt.date

    # Rolling 8-hour averages are calculated across the complete time series,
    # before grouping by date. This preserves windows across midnight.
    air_df["o3_8h_rolling"] = (
        air_df["ozone"].rolling(8, min_periods=8).mean()
    )
    air_df["co_8h_rolling"] = (
        air_df["co"].rolling(8, min_periods=8).mean()
    )

    air_daily = (
        air_df.groupby("date")
        .agg(
            pm2_5_mean=("pm2_5_mean", "mean"),
            pm2_5_max=("pm2_5_mean", "max"),
            pm10_mean=("pm10_mean", "mean"),
            pm10_max=("pm10_mean", "max"),
            no2_mean=("no2_mean", "mean"),
            so2_mean=("so2_mean", "mean"),
            o3_8h_max=("o3_8h_rolling", "max"),
            co_8h_max=("co_8h_rolling", "max"),
            dust_mean=("dust_mean", "mean"),
            aod_mean=("aod_mean", "mean"),
            hours_available=("pm2_5_mean", "count"),
        )
        .reset_index()
    )

    air_daily["date"] = pd.to_datetime(air_daily["date"])
    air_daily["city"] = city_name

    # Fetch daily weather and hourly relative humidity.
    weather_data = fetch_api(
        WEATHER_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "temperature_2m_mean,"
                "apparent_temperature_max,"
                "precipitation_sum,"
                "precipitation_hours,"
                "wind_speed_10m_max,"
                "wind_direction_10m_dominant,"
                "shortwave_radiation_sum,"
                "et0_fao_evapotranspiration,"
                "weather_code"
            ),
            "hourly": "relative_humidity_2m",
            "timezone": TIMEZONE,
            "past_days": 2,
            "forecast_days": 2,
        },
    )

    weather_daily = pd.DataFrame(weather_data["daily"])
    weather_daily["date"] = pd.to_datetime(weather_daily["time"])

    humidity_df = pd.DataFrame({
        "time": weather_data["hourly"]["time"],
        "relative_humidity_2m": weather_data["hourly"]["relative_humidity_2m"],
    })
    humidity_df["date"] = pd.to_datetime(humidity_df["time"]).dt.date

    humidity_daily = (
        humidity_df.groupby("date")["relative_humidity_2m"]
        .mean()
        .reset_index()
    )
    humidity_daily["date"] = pd.to_datetime(humidity_daily["date"])

    weather_daily = weather_daily.merge(
        humidity_daily,
        on="date",
        how="left",
    )
    weather_daily.rename(
        columns={
            "relative_humidity_2m": "relative_humidity_2m_mean",
        },
        inplace=True,
    )

    weather_daily["city"] = city_name
    weather_daily = weather_daily.drop(columns=["time"])

    # Combine air quality and weather records for matching dates.
    combined = air_daily.merge(
        weather_daily,
        on=["date", "city"],
        how="inner",
    )

    if combined.empty:
        raise RuntimeError("No overlapping air-quality and weather dates returned.")

    # Calculate full AQI and PM-only AQI.
    aqi_results = combined.apply(calculate_daily_aqi, axis=1)
    combined = pd.concat([combined, aqi_results], axis=1)

    print(
        f"    Success: {len(combined)} daily records | "
        f"{combined['date'].min().date()} to {combined['date'].max().date()}"
    )

    return combined

def validate_nagpur(combined):
    if not AIR_FILE.exists() or not WEATHER_FILE.exists():
        print("\nOriginal data files not found. Skipping validation.")
        return

    original_air = pd.read_csv(AIR_FILE, parse_dates=["date"])
    original_weather = pd.read_csv(WEATHER_FILE, parse_dates=["date"])

    original = original_air.merge(
        original_weather,
        on=["date", "city"],
        how="inner",
    )

    original_row = original[
        (original["city"].str.lower() == VALIDATION_CITY.lower())
        & (original["date"] == pd.Timestamp(VALIDATION_DATE))
    ]

    api_row = combined[
        (combined["city"].str.lower() == VALIDATION_CITY.lower())
        & (combined["date"] == pd.Timestamp(VALIDATION_DATE))
    ]

    
    print(" NAGPUR NOVEMBER 3 VALIDATION")
    

    if api_row.empty or original_row.empty:
        print("Validation date is unavailable in one of the datasets.")
        return

    feature_columns = [
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

    api_record = api_row.iloc[0]
    original_record = original_row.iloc[0]

    rows = []
    for column in feature_columns:
        api_value = api_record[column]
        original_value = original_record[column]

        rows.append({
            "feature": column,
            "api_value": api_value,
            "original_value": original_value,
            "difference": (
                api_value - original_value
                if pd.notna(api_value) and pd.notna(original_value)
                else None
            ),
        })

    comparison = pd.DataFrame(rows)
    print(comparison.round(3).to_string(index=False))

    print("\nAQI comparison:")
    aqi_columns = [
        "india_aqi",
        "india_aqi_category",
        "india_aqi_pm",
        "india_aqi_pm_category",
        "dominant_pollutant",
    ]

    for column in aqi_columns:
        api_value = api_record[column]
        original_value = original_record[column]
        print(f"{column}: API={api_value} | Original={original_value}")

    comparison.to_csv(VALIDATION_FILE, index=False)
    print(f"\nValidation report saved: {VALIDATION_FILE}")



# MAIN - PROCESS ALL 50 CITIES


def main():
    
    print(" AQI NEXT-GEN - ALL-CITY DAILY DATA UPDATER")
    

    if not CITIES_FILE.exists():
        raise FileNotFoundError(f"Cities file not found: {CITIES_FILE}")

    cities = pd.read_csv(CITIES_FILE)

    required_columns = {"city", "latitude", "longitude"}
    missing_columns = required_columns - set(cities.columns)

    if missing_columns:
        raise ValueError(
            f"cities.csv is missing required columns: {sorted(missing_columns)}"
        )

    cities = cities.dropna(subset=["city", "latitude", "longitude"]).copy()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Cities found: {len(cities)}")
    print("Original CSV files will NOT be modified.")
    print(f"Staging output: {OUTPUT_FILE}")

    successful_frames = []
    errors = []

    for index, (_, city_row) in enumerate(cities.iterrows(), start=1):
        city_name = str(city_row["city"])
        print(f"\n[{index}/{len(cities)}] ", end="")

        try:
            city_data = fetch_city_daily(city_row)
            successful_frames.append(city_data)

        except Exception as exc:
            print(f"\n    FAILED: {city_name} - {exc}")
            errors.append({
                "city": city_name,
                "error": str(exc),
            })

        # Small pause between cities to avoid sending requests too rapidly.
        time.sleep(0.2)

    if successful_frames:
        all_cities = pd.concat(successful_frames, ignore_index=True)

        all_cities["date"] = pd.to_datetime(all_cities["date"])
        all_cities = all_cities.sort_values(
            ["city", "date"]
        ).reset_index(drop=True)

        all_cities.to_csv(OUTPUT_FILE, index=False)

        
        print(" ALL-CITY UPDATE SUMMARY")
        print(f"Cities in source file: {len(cities)}")
        print(f"Cities processed successfully: {len(successful_frames)}")
        print(f"Cities failed: {len(errors)}")
        print(f"Daily records generated: {len(all_cities)}")
        print(f"Unique cities in output: {all_cities['city'].nunique()}")
        print(f"Date range: {all_cities['date'].min().date()} to "
              f"{all_cities['date'].max().date()}")
        print(f"\nSaved staging data: {OUTPUT_FILE}")

        # Confirm the known AQI validation case.
        validate_nagpur(all_cities)

    else:
        print("\nNo city data was successfully collected.")
        print("Check the API connection and city coordinates.")

    if errors:
        pd.DataFrame(errors).to_csv(ERROR_FILE, index=False)
        print(f"\nFailed-city report saved: {ERROR_FILE}")
        print("\nCities requiring retry:")
        for item in errors:
            print(f" - {item['city']}: {item['error']}")
    else:
        # Remove a stale error report from an earlier run, if present.
        if ERROR_FILE.exists():
            ERROR_FILE.unlink()
        print("\nAll cities processed without reported errors.")

    
    print(" DAILY DATA UPDATE FINISHED")
    

if __name__ == "__main__":
    main()
