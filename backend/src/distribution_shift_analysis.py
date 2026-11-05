
from pathlib import Path

import numpy as np
import pandas as pd


# ==================================================
# PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[1]

SPLIT_DIR = ROOT / "data" / "processed" / "splits"

OUTPUT_DIR = (
    ROOT / "data" / "reports" / "distribution_shift"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# CONFIGURATION
# ==================================================

TARGETS = {
    "india_aqi": {
        "column": "target_india_aqi_next_day",
        "label": "Full India AQI",
    },
    "india_aqi_pm": {
        "column": "target_india_aqi_pm_next_day",
        "label": "PM-based AQI",
    },
}

SPLITS = ["train", "validation", "test"]

THRESHOLDS = [200, 300, 400]


# ==================================================
# LOAD DATA
# ==================================================

def load_all_splits():

    frames = []

    for split_name in SPLITS:

        path = SPLIT_DIR / f"{split_name}.csv"

        df = pd.read_csv(
            path,
            parse_dates=["target_date"]
        )

        df["split"] = split_name

        frames.append(df)

    combined = pd.concat(
        frames,
        ignore_index=True
    )

    combined.sort_values(
        ["city", "target_date"],
        inplace=True
    )

    combined.reset_index(drop=True, inplace=True)

    return combined


# ==================================================
# DISTRIBUTION SUMMARY
# ==================================================

def distribution_summary(df, target_column):

    rows = []

    for split_name, group in df.groupby("split"):

        values = group[target_column]

        row = {
            "split": split_name,
            "records": len(group),
            "mean": values.mean(),
            "median": values.median(),
            "std": values.std(),
            "minimum": values.min(),
            "maximum": values.max(),
            "q90": values.quantile(0.90),
            "q95": values.quantile(0.95),
            "q99": values.quantile(0.99),
            "exactly_500": (values == 500).sum(),
            "percentage_exactly_500": (
                (values == 500).mean() * 100
            ),
        }

        for threshold in THRESHOLDS:

            count = (values > threshold).sum()

            row[f"above_{threshold}_count"] = count

            row[f"above_{threshold}_percentage"] = (
                count / len(group) * 100
            )

        rows.append(row)

    return pd.DataFrame(rows)


# ==================================================
# YEARLY DISTRIBUTION
# ==================================================

def yearly_analysis(df, target_column):

    data = df.copy()

    data["year"] = data["target_date"].dt.year

    result = (
        data.groupby(
            ["split", "year"]
        )[target_column]
        .agg(
            records="count",
            mean="mean",
            median="median",
            maximum="max",
        )
        .reset_index()
    )

    for threshold in THRESHOLDS:

        counts = (
            data.assign(
                extreme=data[target_column] > threshold
            )
            .groupby(["split", "year"])["extreme"]
            .sum()
            .rename(f"above_{threshold}_count")
        )

        result = result.merge(
            counts.reset_index(),
            on=["split", "year"],
            how="left"
        )

    return result


# ==================================================
# MONTHLY DISTRIBUTION
# ==================================================

def monthly_analysis(df, target_column):

    data = df.copy()

    data["year"] = data["target_date"].dt.year
    data["month"] = data["target_date"].dt.month

    data["month_name"] = (
        data["target_date"].dt.strftime("%B")
    )

    result = (
        data.groupby(
            ["split", "year", "month", "month_name"]
        )[target_column]
        .agg(
            records="count",
            mean="mean",
            median="median",
            maximum="max",
        )
        .reset_index()
    )

    for threshold in THRESHOLDS:

        counts = (
            data.assign(
                extreme=data[target_column] > threshold
            )
            .groupby(
                ["split", "year", "month"]
            )["extreme"]
            .sum()
            .rename(f"above_{threshold}_count")
        )

        result = result.merge(
            counts.reset_index(),
            on=["split", "year", "month"],
            how="left"
        )

    return result


# ==================================================
# CITY-WISE DISTRIBUTION
# ==================================================

def city_analysis(df, target_column):

    data = df.copy()

    rows = []

    for (split_name, city), group in data.groupby(
        ["split", "city"]
    ):

        values = group[target_column]

        row = {
            "split": split_name,
            "city": city,
            "records": len(group),
            "mean": values.mean(),
            "median": values.median(),
            "maximum": values.max(),
            "exactly_500": (values == 500).sum(),
        }

        for threshold in THRESHOLDS:

            count = (values > threshold).sum()

            row[f"above_{threshold}_count"] = count

            row[f"above_{threshold}_percentage"] = (
                count / len(group) * 100
            )

        rows.append(row)

    return pd.DataFrame(rows)


# ==================================================
# EXTREME OBSERVATION DETAILS
# ==================================================

def extreme_observations(df, target_column):

    rows = []

    for threshold in THRESHOLDS:

        subset = df[
            df[target_column] > threshold
        ].copy()

        if subset.empty:
            continue

        subset["threshold"] = threshold

        rows.append(
            subset[
                [
                    "split",
                    "city",
                    "target_date",
                    target_column,
                    "threshold",
                ]
            ]
        )

    if not rows:
        return pd.DataFrame()

    return pd.concat(
        rows,
        ignore_index=True
    )


# ==================================================
# CONSECUTIVE EXTREME EVENTS
# ==================================================

def consecutive_events(df, target_column):

    data = df[
        [
            "city",
            "target_date",
            target_column,
        ]
    ].copy()

    data.sort_values(
        ["city", "target_date"],
        inplace=True
    )

    events = []

    for threshold in THRESHOLDS:

        subset = data[
            data[target_column] > threshold
        ].copy()

        if subset.empty:
            continue

        # Separate events when there is a date gap
        # or when a city changes.
        date_gap = (
            subset.groupby("city")["target_date"]
            .diff()
            .dt.days
        )

        new_event = (
            date_gap.isna() | (date_gap != 1)
        )

        subset["event_id"] = (
            new_event.groupby(subset["city"])
            .cumsum()
        )

        for (city, event_id), group in subset.groupby(
            ["city", "event_id"]
        ):

            start_date = group["target_date"].min()
            end_date = group["target_date"].max()

            duration = (
                end_date - start_date
            ).days + 1

            events.append({
                "city": city,
                "threshold": threshold,
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": duration,
                "record_count": len(group),
                "mean_aqi": group[target_column].mean(),
                "maximum_aqi": group[target_column].max(),
            })

    return pd.DataFrame(events)


# ==================================================
# SPLIT COMPARISON
# ==================================================

def compare_split_distributions(summary):

    rows = []

    for threshold in THRESHOLDS:

        column = f"above_{threshold}_percentage"

        train_value = summary.loc[
            summary["split"] == "train",
            column
        ].iloc[0]

        validation_value = summary.loc[
            summary["split"] == "validation",
            column
        ].iloc[0]

        test_value = summary.loc[
            summary["split"] == "test",
            column
        ].iloc[0]

        rows.append({
            "threshold": threshold,
            "train_percentage": train_value,
            "validation_percentage": validation_value,
            "test_percentage": test_value,
            "test_minus_train_percentage_points": (
                test_value - train_value
            ),
        })

    return pd.DataFrame(rows)


# ==================================================
# PROCESS ONE TARGET
# ==================================================

def analyze_target(df, target_name, config):

    target_column = config["column"]

    print("\n" + "=" * 70)
    print(f"DISTRIBUTION SHIFT: {config['label']}")
    print("=" * 70)

    # 1. Overall split summary
    summary = distribution_summary(
        df,
        target_column
    )

    summary.to_csv(
        OUTPUT_DIR / f"{target_name}_split_summary.csv",
        index=False
    )

    print("\nSPLIT DISTRIBUTION")
    print(summary.to_string(index=False))

    # 2. Train vs validation vs test comparison
    comparison = compare_split_distributions(
        summary
    )

    comparison.to_csv(
        OUTPUT_DIR / f"{target_name}_shift_comparison.csv",
        index=False
    )

    print("\nEXTREME FREQUENCY SHIFT")
    print(comparison.to_string(index=False))

    # 3. Yearly analysis
    yearly = yearly_analysis(
        df,
        target_column
    )

    yearly.to_csv(
        OUTPUT_DIR / f"{target_name}_yearly_distribution.csv",
        index=False
    )

    print("\nYEARLY DISTRIBUTION")
    print(yearly.to_string(index=False))

    # 4. Monthly analysis
    monthly = monthly_analysis(
        df,
        target_column
    )

    monthly.to_csv(
        OUTPUT_DIR / f"{target_name}_monthly_distribution.csv",
        index=False
    )

    # 5. City-wise analysis
    cities = city_analysis(
        df,
        target_column
    )

    cities.to_csv(
        OUTPUT_DIR / f"{target_name}_city_distribution.csv",
        index=False
    )

    print("\nCITIES WITH MOST OBSERVATIONS ABOVE 300 IN TEST")

    worst_cities = (
        cities[cities["split"] == "test"]
        .sort_values(
            "above_300_count",
            ascending=False
        )
        .head(15)
    )

    print(worst_cities.to_string(index=False))

    # 6. Extreme observation details
    extremes = extreme_observations(
        df,
        target_column
    )

    extremes.to_csv(
        OUTPUT_DIR / f"{target_name}_extreme_observations.csv",
        index=False
    )

    # 7. Consecutive extreme episodes
    events = consecutive_events(
        df,
        target_column
    )

    events.to_csv(
        OUTPUT_DIR / f"{target_name}_consecutive_events.csv",
        index=False
    )

    print("\nCONSECUTIVE EXTREME EVENTS")

    if not events.empty:

        print(
            events.sort_values(
                "maximum_aqi",
                ascending=False
            ).head(15).to_string(index=False)
        )

    # 8. Exact AQI 500 observations
    capped = df[
        df[target_column] == 500
    ][
        [
            "split",
            "city",
            "target_date",
            target_column,
        ]
    ].copy()

    capped.to_csv(
        OUTPUT_DIR / f"{target_name}_aqi_500_records.csv",
        index=False
    )

    print("\nEXACT AQI 500 RECORDS")
    print(f"Total: {len(capped)}")

    if not capped.empty:

        print(
            capped.groupby(
                ["split", "city"]
            ).size()
            .sort_values(ascending=False)
            .head(15)
        )

    return {
        "target": target_name,
        "total_records": len(df),
        "train_above_300": int(
            summary.loc[
                summary["split"] == "train",
                "above_300_count"
            ].iloc[0]
        ),
        "validation_above_300": int(
            summary.loc[
                summary["split"] == "validation",
                "above_300_count"
            ].iloc[0]
        ),
        "test_above_300": int(
            summary.loc[
                summary["split"] == "test",
                "above_300_count"
            ].iloc[0]
        ),
        "test_exactly_500": len(capped[
            capped["split"] == "test"
        ]),
    }


# ==================================================
# MAIN
# ==================================================

def main():

    print("AQI TEMPORAL AND DISTRIBUTION SHIFT ANALYSIS")
    print("=" * 70)

    df = load_all_splits()

    print(f"\nTotal records: {len(df):,}")
    print(f"Unique cities: {df['city'].nunique()}")
    print(
        f"Target date range: "
        f"{df['target_date'].min().date()} to "
        f"{df['target_date'].max().date()}"
    )

    if df.duplicated(["city", "target_date"]).any():
        raise ValueError(
            "Duplicate city-target-date records found."
        )

    summaries = []

    for target_name, config in TARGETS.items():

        summary = analyze_target(
            df,
            target_name,
            config
        )

        summaries.append(summary)

    final_summary = pd.DataFrame(summaries)

    final_summary.to_csv(
        OUTPUT_DIR / "distribution_shift_summary.csv",
        index=False
    )

    report_path = (
        OUTPUT_DIR / "distribution_shift_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "AQI TEMPORAL AND DISTRIBUTION SHIFT REPORT\n"
        )

        file.write("=" * 70 + "\n\n")

        file.write(
            f"Total records: {len(df):,}\n"
        )

        file.write(
            f"Unique cities: {df['city'].nunique()}\n"
        )

        file.write(
            f"Target date range: "
            f"{df['target_date'].min().date()} to "
            f"{df['target_date'].max().date()}\n\n"
        )

        file.write(
            final_summary.to_string(
                index=False
            )
        )

        file.write("\n\n")

        file.write(
            "AQI 500 is examined as an exact recorded value. "
            "Its presence alone does not prove that a record "
            "is erroneous or that the underlying pollutant "
            "concentration was capped.\n"
        )

    print("\n" + "=" * 70)
    print("DISTRIBUTION SHIFT ANALYSIS COMPLETED")
    print("=" * 70)

    print(final_summary.to_string(index=False))

    print(f"\nAll outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
