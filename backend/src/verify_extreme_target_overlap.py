
from pathlib import Path

import pandas as pd



# PATHS


ROOT = Path(__file__).resolve().parents[1]

SPLIT_DIR = ROOT / "data" / "processed" / "splits"

OUTPUT_DIR = (
    ROOT / "data" / "reports" / "target_overlap"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



# CONFIGURATION


FULL_TARGET = "target_india_aqi_next_day"
PM_TARGET = "target_india_aqi_pm_next_day"

KEY_COLUMNS = ["city", "target_date"]



# LOAD DATA


def load_splits():

    frames = []

    for split_name in ["train", "validation", "test"]:

        path = SPLIT_DIR / f"{split_name}.csv"

        df = pd.read_csv(
            path,
            parse_dates=["target_date"]
        )

        df["split"] = split_name

        frames.append(df)

    data = pd.concat(
        frames,
        ignore_index=True
    )

    return data



# PREPARE TARGET DATA


def prepare_data(data):

    required_columns = (
        KEY_COLUMNS
        + ["split", FULL_TARGET, PM_TARGET]
    )

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    targets = data[required_columns].copy()

    if targets.duplicated(KEY_COLUMNS).any():
        raise ValueError(
            "Duplicate city-target_date records detected."
        )

    return targets



# OVERLAP ANALYSIS


def analyze_overlap(data):

    print("\n" + "=" * 70)
    print("EXTREME TARGET OVERLAP ANALYSIS")
    print("=" * 70)

    results = []

    for threshold in [300, 400, 500]:

        full_extreme = data[FULL_TARGET] >= threshold
        pm_extreme = data[PM_TARGET] >= threshold

        both = full_extreme & pm_extreme
        full_only = full_extreme & ~pm_extreme
        pm_only = pm_extreme & ~full_extreme

        result = {
            "threshold": threshold,
            "full_target_extreme_count": int(
                full_extreme.sum()
            ),
            "pm_target_extreme_count": int(
                pm_extreme.sum()
            ),
            "both_extreme_count": int(both.sum()),
            "full_only_count": int(full_only.sum()),
            "pm_only_count": int(pm_only.sum()),
        }

        results.append(result)

    summary = pd.DataFrame(results)

    print("\nOVERALL EXTREME OVERLAP")
    print(summary.to_string(index=False))

    summary.to_csv(
        OUTPUT_DIR / "extreme_overlap_summary.csv",
        index=False
    )

    return summary



# EXACT AQI 500 COMPARISON


def analyze_exact_500(data):

    full_500 = data[FULL_TARGET] == 500
    pm_500 = data[PM_TARGET] == 500

    both_500 = full_500 & pm_500
    full_only = full_500 & ~pm_500
    pm_only = pm_500 & ~full_500

    print("\n" + "=" * 70)
    print("EXACT AQI 500 COMPARISON")
    print("=" * 70)

    print(f"Full AQI exactly 500: {full_500.sum()}")
    print(f"PM AQI exactly 500: {pm_500.sum()}")
    print(f"Both exactly 500: {both_500.sum()}")
    print(f"Only full AQI 500: {full_only.sum()}")
    print(f"Only PM AQI 500: {pm_only.sum()}")

    # Save every observation where at least one target is 500.
    records = data[
        full_500 | pm_500
    ].copy()

    records["full_is_500"] = full_500[
        full_500 | pm_500
    ].values

    records["pm_is_500"] = pm_500[
        full_500 | pm_500
    ].values

    records.to_csv(
        OUTPUT_DIR / "exact_500_records.csv",
        index=False
    )

    # City-wise exact 500 overlap
    city_summary = (
        records.groupby("city")
        .agg(
            full_500_count=("full_is_500", "sum"),
            pm_500_count=("pm_is_500", "sum"),
        )
        .reset_index()
    )

    city_summary.to_csv(
        OUTPUT_DIR / "exact_500_city_summary.csv",
        index=False
    )

    # Split-wise exact 500 overlap
    split_summary = (
        records.groupby("split")
        .agg(
            full_500_count=("full_is_500", "sum"),
            pm_500_count=("pm_is_500", "sum"),
        )
        .reset_index()
    )

    split_summary.to_csv(
        OUTPUT_DIR / "exact_500_split_summary.csv",
        index=False
    )

    return records



# ABOVE 400 CITY-DATE OVERLAP


def analyze_above_400(data):

    full_extreme = data[FULL_TARGET] > 400
    pm_extreme = data[PM_TARGET] > 400

    both = full_extreme & pm_extreme
    full_only = full_extreme & ~pm_extreme
    pm_only = pm_extreme & ~full_extreme

    records = data[
        full_extreme | pm_extreme
    ].copy()

    records["full_above_400"] = full_extreme[
        full_extreme | pm_extreme
    ].values

    records["pm_above_400"] = pm_extreme[
        full_extreme | pm_extreme
    ].values

    records["overlap"] = both[
        full_extreme | pm_extreme
    ].values

    records.to_csv(
        OUTPUT_DIR / "above_400_city_date_records.csv",
        index=False
    )

    print("\n" + "=" * 70)
    print("ABOVE 400 CITY-DATE OVERLAP")
    print("=" * 70)

    print(f"Full AQI above 400: {full_extreme.sum()}")
    print(f"PM AQI above 400: {pm_extreme.sum()}")
    print(f"Both above 400: {both.sum()}")
    print(f"Only full AQI above 400: {full_only.sum()}")
    print(f"Only PM AQI above 400: {pm_only.sum()}")

    # City-wise overlap
    city_summary = (
        records.groupby("city")
        .agg(
            full_above_400=("full_above_400", "sum"),
            pm_above_400=("pm_above_400", "sum"),
            overlap=("overlap", "sum"),
        )
        .reset_index()
    )

    city_summary.to_csv(
        OUTPUT_DIR / "above_400_city_summary.csv",
        index=False
    )

    # Split-wise overlap
    split_summary = (
        records.groupby("split")
        .agg(
            full_above_400=("full_above_400", "sum"),
            pm_above_400=("pm_above_400", "sum"),
            overlap=("overlap", "sum"),
        )
        .reset_index()
    )

    split_summary.to_csv(
        OUTPUT_DIR / "above_400_split_summary.csv",
        index=False
    )

    return records



# TARGET CORRELATION AT EXTREME VALUES


def analyze_extreme_values(data):

    print("\n" + "=" * 70)
    print("TARGET RELATIONSHIP AT EXTREME VALUES")
    print("=" * 70)

    for threshold in [300, 400]:

        subset = data[
            (data[FULL_TARGET] >= threshold)
            | (data[PM_TARGET] >= threshold)
        ]

        print(f"\nRecords with either target >= {threshold}:")
        print(f"Count: {len(subset)}")

        if len(subset) > 1:

            print(
                "Correlation:",
                round(
                    subset[FULL_TARGET].corr(
                        subset[PM_TARGET]
                    ),
                    4
                )
            )

            print(
                "Mean absolute target difference:",
                round(
                    (
                        subset[FULL_TARGET]
                        - subset[PM_TARGET]
                    ).abs().mean(),
                    2
                )
            )



# MAIN


def main():

    print("Loading chronological split datasets...")

    data = load_splits()

    data = prepare_data(data)

    print(f"Total records: {len(data):,}")
    print(f"Unique cities: {data['city'].nunique()}")

    print(
        f"Date range: "
        f"{data['target_date'].min().date()} to "
        f"{data['target_date'].max().date()}"
    )

    analyze_overlap(data)

    analyze_exact_500(data)

    analyze_above_400(data)

    analyze_extreme_values(data)

    print("\n" + "=" * 70)
    print("TARGET OVERLAP ANALYSIS COMPLETED")
    print("=" * 70)

    print(f"Reports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
    