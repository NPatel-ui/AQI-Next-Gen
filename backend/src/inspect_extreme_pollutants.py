
from pathlib import Path

import pandas as pd



# PATHS


ROOT = Path(__file__).resolve().parents[1]

MERGED_FILE = (
    ROOT / "data" / "processed" / "merged_daily.csv"
)

EXTREME_FILE = (
    ROOT
    / "data"
    / "reports"
    / "target_overlap"
    / "above_400_city_date_records.csv"
)

OUTPUT_DIR = (
    ROOT / "data" / "reports" / "extreme_pollutants"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



# REQUIRED COLUMNS


POLLUTANT_COLUMNS = [
    "pm2_5_mean",
    "pm2_5_max",
    "pm10_mean",
    "pm10_max",
    "o3_8h_max",
    "no2_mean",
    "so2_mean",
    "co_8h_max",
    "dust_mean",
    "aod_mean",
    "us_aqi_max",
    "hours_available",
    "india_aqi",
    "india_aqi_pm",
    "india_aqi_category",
    "india_aqi_pm_category",
    "dominant_pollutant",
]

KEY_COLUMNS = ["city", "date"]



# LOAD DATA


def load_data():

    print("Loading merged dataset...")

    merged = pd.read_csv(
        MERGED_FILE,
        parse_dates=["date"]
    )

    print("Loading extreme city-date records...")

    extreme = pd.read_csv(
        EXTREME_FILE,
        parse_dates=["target_date"]
    )

    return merged, extreme



# VALIDATE DATA


def validate_data(merged, extreme):

    missing_merged = [
        col for col in KEY_COLUMNS + POLLUTANT_COLUMNS
        if col not in merged.columns
    ]

    if missing_merged:
        raise ValueError(
            f"Missing columns in merged dataset: {missing_merged}"
        )

    missing_extreme = [
        col for col in ["city", "target_date"]
        if col not in extreme.columns
    ]

    if missing_extreme:
        raise ValueError(
            f"Missing columns in extreme dataset: {missing_extreme}"
        )

    if merged.duplicated(KEY_COLUMNS).any():
        raise ValueError(
            "Duplicate city-date records found in merged dataset."
        )



# JOIN EXTREME DATES WITH POLLUTANTS


def extract_pollutants(merged, extreme):

    print("\nMatching extreme records with pollutant measurements...")

    extreme_keys = extreme[
        ["city", "target_date"]
    ].drop_duplicates().copy()

    extreme_keys = extreme_keys.rename(
        columns={"target_date": "date"}
    )

    result = extreme_keys.merge(
        merged[KEY_COLUMNS + POLLUTANT_COLUMNS],
        on=KEY_COLUMNS,
        how="left",
        validate="one_to_one",
        indicator=True
    )

    unmatched = result["_merge"] != "both"

    print(f"Extreme city-date records: {len(extreme_keys):,}")
    print(f"Successfully matched: {(~unmatched).sum():,}")
    print(f"Unmatched records: {unmatched.sum():,}")

    result = result.drop(columns="_merge")

    result = result.merge(
        extreme,
        left_on=["city", "date"],
        right_on=["city", "target_date"],
        how="left",
        validate="one_to_one"
    )

    return result



# POLLUTANT SUMMARY


def generate_summary(data):

    print("\nGenerating pollutant statistics...")

    numeric_columns = [
        "pm2_5_mean",
        "pm2_5_max",
        "pm10_mean",
        "pm10_max",
        "o3_8h_max",
        "no2_mean",
        "so2_mean",
        "co_8h_max",
        "dust_mean",
        "aod_mean",
        "us_aqi_max",
        "hours_available",
        "india_aqi",
        "india_aqi_pm",
    ]

    summary = (
        data[numeric_columns]
        .describe()
        .T
        .reset_index()
        .rename(columns={"index": "parameter"})
    )

    summary.to_csv(
        OUTPUT_DIR / "extreme_pollutant_statistics.csv",
        index=False
    )

    return summary



# CITY-WISE ANALYSIS


def city_analysis(data):

    city_summary = (
        data.groupby("city")
        .agg(
            extreme_records=("city", "size"),
            full_aqi_mean=("india_aqi", "mean"),
            pm_aqi_mean=("india_aqi_pm", "mean"),
            pm25_mean=("pm2_5_mean", "mean"),
            pm10_mean=("pm10_mean", "mean"),
            ozone_mean=("o3_8h_max", "mean"),
            no2_mean=("no2_mean", "mean"),
            so2_mean=("so2_mean", "mean"),
            co_mean=("co_8h_max", "mean"),
            hours_available_mean=("hours_available", "mean"),
        )
        .reset_index()
        .sort_values("extreme_records", ascending=False)
    )

    city_summary.to_csv(
        OUTPUT_DIR / "extreme_pollutants_by_city.csv",
        index=False
    )

    return city_summary



# DOMINANT POLLUTANT ANALYSIS


def dominant_pollutant_analysis(data):

    summary = (
        data["dominant_pollutant"]
        .value_counts(dropna=False)
        .rename_axis("dominant_pollutant")
        .reset_index(name="record_count")
    )

    summary.to_csv(
        OUTPUT_DIR / "extreme_dominant_pollutants.csv",
        index=False
    )

    return summary



# AQI 500 ANALYSIS


def analyze_500_records(data):

    records_500 = data[
        (data["india_aqi"] == 500)
        | (data["india_aqi_pm"] == 500)
    ].copy()

    records_500.to_csv(
        OUTPUT_DIR / "aqi_500_pollutant_records.csv",
        index=False
    )

    print("\nEXACT 500 RECORDS")
    print(f"Records: {len(records_500):,}")

    if not records_500.empty:

        print("\nDominant pollutant distribution:")

        print(
            records_500["dominant_pollutant"]
            .value_counts(dropna=False)
            .to_string()
        )

        print("\nPollutant averages:")

        columns = [
            "pm2_5_mean",
            "pm10_mean",
            "o3_8h_max",
            "no2_mean",
            "so2_mean",
            "co_8h_max",
            "us_aqi_max",
        ]

        print(
            records_500[columns]
            .describe()
            .round(2)
            .to_string()
        )

    return records_500



# TARGET EQUALITY VERIFICATION


def verify_target_equality(data):

    data["target_difference"] = (
        data["target_india_aqi_next_day"]
        - data["target_india_aqi_pm_next_day"]
    )

    print("\nTARGET DIFFERENCE ON EXTREME RECORDS")

    print(
        data["target_difference"]
        .describe()
        .round(2)
        .to_string()
    )

    data.to_csv(
        OUTPUT_DIR / "extreme_pollutant_records.csv",
        index=False
    )



# MAIN


def main():

    merged, extreme = load_data()

    validate_data(merged, extreme)

    data = extract_pollutants(
        merged,
        extreme
    )

    if data["pm2_5_mean"].isna().any():
        raise ValueError(
            "Some extreme records could not be matched. "
            "Check the date alignment before proceeding."
        )

    print("\n" + "=" * 70)
    print("EXTREME POLLUTANT INVESTIGATION")
    print("=" * 70)

    print(f"Matched records: {len(data):,}")
    print(f"Unique cities: {data['city'].nunique()}")

    print("\nDOMINANT POLLUTANT DISTRIBUTION")

    print(
        data["dominant_pollutant"]
        .value_counts(dropna=False)
        .to_string()
    )

    summary = generate_summary(data)

    print("\nPOLLUTANT STATISTICS")
    print(
        summary.round(2).to_string(index=False)
    )

    city_summary = city_analysis(data)

    print("\nTOP CITIES BY EXTREME RECORDS")
    print(
        city_summary.head(15)
        .round(2)
        .to_string(index=False)
    )

    dominant_pollutant_analysis(data)

    analyze_500_records(data)

    verify_target_equality(data)

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETED")
    print("=" * 70)

    print(f"Reports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
