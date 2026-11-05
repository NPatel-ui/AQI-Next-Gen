
from pathlib import Path

import pandas as pd



# PATHS


ROOT = Path(__file__).resolve().parents[1]

MERGED_FILE = ROOT / "data" / "processed" / "merged_daily.csv"

SPLIT_DIR = ROOT / "data" / "processed" / "splits"

OUTPUT_DIR = ROOT / "data" / "reports" / "pm10_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



# LOAD DATA


def load_data():

    merged = pd.read_csv(
        MERGED_FILE,
        parse_dates=["date"]
    )

    frames = []

    for split in ["train", "validation", "test"]:

        df = pd.read_csv(
            SPLIT_DIR / f"{split}.csv",
            parse_dates=["target_date"]
        )

        df["split"] = split

        frames.append(
            df[["city", "target_date", "split"]]
        )

    split_data = pd.concat(
        frames,
        ignore_index=True
    )

    split_data = split_data.rename(
        columns={"target_date": "date"}
    )

    data = merged.merge(
        split_data,
        on=["city", "date"],
        how="inner",
        validate="one_to_one"
    )

    return data



# DISTRIBUTION SUMMARY


def distribution_summary(data, group_columns):

    result = (
        data.groupby(group_columns)
        .agg(
            records=("pm10_mean", "size"),
            mean=("pm10_mean", "mean"),
            median=("pm10_mean", "median"),
            std=("pm10_mean", "std"),
            p90=("pm10_mean", lambda x: x.quantile(0.90)),
            p95=("pm10_mean", lambda x: x.quantile(0.95)),
            p99=("pm10_mean", lambda x: x.quantile(0.99)),
            maximum=("pm10_mean", "max"),
            above_100=("pm10_mean", lambda x: (x > 100).sum()),
            above_250=("pm10_mean", lambda x: (x > 250).sum()),
            above_500=("pm10_mean", lambda x: (x > 500).sum()),
        )
        .reset_index()
    )

    return result



# SPLIT ANALYSIS


def analyze_splits(data):

    summary = distribution_summary(
        data,
        ["split"]
    )

    summary.to_csv(
        OUTPUT_DIR / "pm10_by_split.csv",
        index=False
    )

    print("\nPM10 DISTRIBUTION BY SPLIT")
    print(summary.round(2).to_string(index=False))



# YEARLY ANALYSIS


def analyze_yearly(data):

    data = data.copy()

    data["year"] = data["date"].dt.year

    summary = distribution_summary(
        data,
        ["split", "year"]
    )

    summary.to_csv(
        OUTPUT_DIR / "pm10_by_year.csv",
        index=False
    )

    print("\nPM10 DISTRIBUTION BY YEAR")
    print(summary.round(2).to_string(index=False))



# MONTHLY ANALYSIS


def analyze_monthly(data):

    data = data.copy()

    data["year_month"] = (
        data["date"].dt.to_period("M").astype(str)
    )

    summary = distribution_summary(
        data,
        ["split", "year_month"]
    )

    summary.to_csv(
        OUTPUT_DIR / "pm10_by_month.csv",
        index=False
    )

    print("\nPM10 DISTRIBUTION BY MONTH")
    print(summary.round(2).to_string(index=False))



# CITY ANALYSIS


def analyze_cities(data):

    summary = distribution_summary(
        data,
        ["city"]
    )

    summary = summary.sort_values(
        "mean",
        ascending=False
    )

    summary.to_csv(
        OUTPUT_DIR / "pm10_by_city.csv",
        index=False
    )

    print("\nTOP 15 CITIES BY AVERAGE PM10")

    print(
        summary.head(15)
        .round(2)
        .to_string(index=False)
    )



# AQI RELATIONSHIP


def analyze_aqi_relationship(data):

    data = data.copy()

    data["aqi_group"] = pd.cut(
        data["india_aqi_pm"],
        bins=[-1, 50, 100, 200, 300, 400, 500],
        labels=[
            "Good",
            "Satisfactory",
            "Moderate",
            "Poor",
            "Very Poor",
            "Severe"
        ],
        include_lowest=True
    )

    summary = (
        data.groupby(
            "aqi_group",
            observed=False
        )
        .agg(
            records=("pm10_mean", "size"),
            pm10_mean=("pm10_mean", "mean"),
            pm10_median=("pm10_mean", "median"),
            pm10_max=("pm10_mean", "max"),
        )
        .reset_index()
    )

    summary.to_csv(
        OUTPUT_DIR / "pm10_by_aqi_category.csv",
        index=False
    )

    print("\nPM10 BY PM-BASED AQI CATEGORY")
    print(summary.round(2).to_string(index=False))



# CITY-SPECIFIC EXTREME RECORDS


def analyze_extreme_cities(data):

    extreme = data[
        (data["pm10_mean"] > 500)
        | (data["india_aqi_pm"] >= 400)
    ].copy()

    extreme = extreme.sort_values(
        "pm10_mean",
        ascending=False
    )

    columns = [
        "date",
        "city",
        "split",
        "pm10_mean",
        "pm10_max",
        "pm2_5_mean",
        "india_aqi",
        "india_aqi_pm",
        "dominant_pollutant"
    ]

    extreme[columns].to_csv(
        OUTPUT_DIR / "extreme_pm10_records.csv",
        index=False
    )

    print("\nEXTREME PM10 RECORDS")
    print(f"Total records: {len(extreme):,}")

    print("\nTop 20 observations:")

    print(
        extreme[columns]
        .head(20)
        .to_string(index=False)
    )



# MAIN


def main():

    print("=" * 70)
    print("PM10 TEMPORAL DISTRIBUTION ANALYSIS")
    print("=" * 70)

    data = load_data()

    print(f"\nTotal records: {len(data):,}")
    print(f"Unique cities: {data['city'].nunique()}")
    print(
        f"Date range: {data['date'].min().date()} "
        f"to {data['date'].max().date()}"
    )

    print(
        f"Missing PM10 values: "
        f"{data['pm10_mean'].isna().sum()}"
    )

    analyze_splits(data)

    analyze_yearly(data)

    analyze_monthly(data)

    analyze_cities(data)

    analyze_aqi_relationship(data)

    analyze_extreme_cities(data)

    print("\n" + "=" * 70)
    print("PM10 ANALYSIS COMPLETED")
    print("=" * 70)

    print(f"Reports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
