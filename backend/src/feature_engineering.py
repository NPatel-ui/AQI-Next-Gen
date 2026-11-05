
from pathlib import Path
import numpy as np
import pandas as pd



# PATHS


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "merged_daily.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "forecasting_dataset.csv"
REPORT_FILE = ROOT / "data" / "reports" / "feature_engineering_report.txt"



# FEATURE CONFIGURATION


# AQI and pollutant measurements available on forecast issue day
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

# Weather measurements available on forecast issue day
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


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("Loading merged dataset...")

    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

    required_columns = {
        "date",
        "city",
        "india_aqi",
        "india_aqi_pm",
    }

    missing_required = required_columns - set(df.columns)

    if missing_required:
        raise ValueError(
            f"Missing required columns: {missing_required}"
        )

    df = df.sort_values(
        ["city", "date"]
    ).reset_index(drop=True)

    if df.duplicated(["city", "date"]).any():
        raise ValueError("Duplicate city-date records found.")

    # Keep only features that actually exist in the dataset.
    pollution_features = [
        col for col in POLLUTION_COLUMNS
        if col in df.columns
    ]

    weather_features = [
        col for col in WEATHER_COLUMNS
        if col in df.columns
    ]

    print(f"Cities: {df['city'].nunique()}")
    print(f"Records: {len(df):,}")
    print(f"Pollution variables: {len(pollution_features)}")
    print(f"Weather variables: {len(weather_features)}")

    
    # 1. CURRENT-DAY FEATURES
    

    print("\nCreating current-day features...")

    # Today's weather and pollution values are available
    # when the forecast is issued after today's data is ready.

    feature_columns = pollution_features + weather_features

    
    # 2. LAG FEATURES
    

    print("Creating lag features...")

    grouped = df.groupby("city", sort=False)

    for col in pollution_features:
        for lag in LAG_PERIODS:
            feature_name = f"{col}_lag_{lag}"

            df[feature_name] = grouped[col].shift(lag)
            feature_columns.append(feature_name)

    
    # 3. ROLLING STATISTICS
    

    print("Creating rolling statistics...")

    for col in pollution_features:

        for window in ROLLING_WINDOWS:

            mean_name = f"{col}_rolling_mean_{window}"
            std_name = f"{col}_rolling_std_{window}"

            df[mean_name] = (
                df.groupby("city", sort=False)[col]
                .transform(
                    lambda s: s.rolling(
                        window=window,
                        min_periods=window
                    ).mean()
                )
            )

            df[std_name] = (
                df.groupby("city", sort=False)[col]
                .transform(
                    lambda s: s.rolling(
                        window=window,
                        min_periods=window
                    ).std()
                )
            )

            feature_columns.extend([
                mean_name,
                std_name,
            ])

    
    # 4. CALENDAR FEATURES
    

    print("Creating calendar features...")

    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_year"] = df["date"].dt.dayofyear

    df["month_sin"] = np.sin(
        2 * np.pi * df["month"] / 12
    )

    df["month_cos"] = np.cos(
        2 * np.pi * df["month"] / 12
    )

    df["day_of_year_sin"] = np.sin(
        2 * np.pi * df["day_of_year"] / 365.25
    )

    df["day_of_year_cos"] = np.cos(
        2 * np.pi * df["day_of_year"] / 365.25
    )

    feature_columns.extend([
        "month",
        "day_of_week",
        "day_of_year",
        "month_sin",
        "month_cos",
        "day_of_year_sin",
        "day_of_year_cos",
    ])

    
    # 5. NEXT-DAY TARGETS
    

    print("Creating next-day targets...")

    grouped = df.groupby("city", sort=False)

    df["target_india_aqi_next_day"] = (
        grouped["india_aqi"].shift(-1)
    )

    df["target_india_aqi_pm_next_day"] = (
        grouped["india_aqi_pm"].shift(-1)
    )

    df["target_date"] = (
        grouped["date"].shift(-1)
    )

    # Ensure the target is exactly the next calendar day.
    valid_next_day = (
        df["target_date"] - df["date"]
    ).dt.days == 1

    df = df[valid_next_day].copy()

    
    # 6. REMOVE ROWS WITHOUT REQUIRED HISTORY
    

    print("Removing rows without sufficient history...")

    target_columns = [
        "target_india_aqi_next_day",
        "target_india_aqi_pm_next_day",
    ]

    required_features = list(dict.fromkeys(feature_columns))

    before = len(df)

    df = df.dropna(
        subset=required_features + target_columns
    ).copy()

    removed = before - len(df)

    
    # 7. FINAL DATASET
    

    # Keep identifiers, metadata, features and both targets.
    metadata_columns = [
        col for col in [
            "date",
            "target_date",
            "city",
            "state",
            "region",
            "latitude",
            "longitude",
            "elevation",
        ]
        if col in df.columns
    ]

    final_columns = (
        metadata_columns
        + required_features
        + target_columns
    )

    final_columns = list(dict.fromkeys(final_columns))

    final_df = df[final_columns].copy()

    final_df.sort_values(
        ["city", "date"],
        inplace=True
    )

    final_df.reset_index(drop=True, inplace=True)

    
    # 8. VALIDATION
    

    print("\nValidating forecasting dataset...")

    if final_df.isna().any().any():
        raise ValueError(
            "Missing values remain in the final dataset."
        )

    if final_df.duplicated(["city", "date"]).any():
        raise ValueError(
            "Duplicate city-date records found."
        )

    if not (
        final_df["target_date"] - final_df["date"]
    ).dt.days.eq(1).all():
        raise ValueError(
            "Some target dates are not exactly one day ahead."
        )

    
    # 9. SAVE DATASET
    

    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    report = []

    report.append("FEATURE ENGINEERING REPORT")
    report.append("=" * 50)
    report.append(f"Original records: {len(pd.read_csv(INPUT_FILE)):,}")
    report.append(f"Final records: {len(final_df):,}")
    report.append(f"Removed records: {removed:,}")
    report.append(f"Cities: {final_df['city'].nunique()}")
    report.append(f"Final columns: {len(final_df.columns)}")
    report.append(
        f"Forecast origin: {final_df['date'].min().date()} "
        f"to {final_df['date'].max().date()}"
    )
    report.append(
        f"Target date range: {final_df['target_date'].min().date()} "
        f"to {final_df['target_date'].max().date()}"
    )
    report.append(
        f"Missing values: {final_df.isna().sum().sum()}"
    )
    report.append(
        f"Duplicate city-date records: "
        f"{final_df.duplicated(['city', 'date']).sum()}"
    )
    report.append(
        f"Number of model features: {len(required_features)}"
    )
    report.append(
        "Targets: target_india_aqi_next_day, "
        "target_india_aqi_pm_next_day"
    )

    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\nFEATURE ENGINEERING COMPLETED")
    print("=" * 45)
    print(f"Original records: {before + removed:,}")
    print(f"Final records: {len(final_df):,}")
    print(f"Removed records: {removed:,}")
    print(f"Final columns: {len(final_df.columns)}")
    print(f"Model features: {len(required_features)}")
    print(f"Cities: {final_df['city'].nunique()}")
    print(f"Missing values: {final_df.isna().sum().sum()}")
    print(f"Duplicate records: "
          f"{final_df.duplicated(['city', 'date']).sum()}")
    print(f"\nDataset saved: {OUTPUT_FILE}")
    print(f"Report saved: {REPORT_FILE}")


if __name__ == "__main__":
    main()
