
from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "forecasting_dataset.csv"

SPLIT_DIR = ROOT / "data" / "processed" / "splits"
REPORT_DIR = ROOT / "data" / "reports"

REPORT_FILE = REPORT_DIR / "data_split_report.txt"

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


def main():

    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading forecasting dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["date", "target_date"]
    )

    # Basic validation
    required_columns = [
        "date",
        "target_date",
        "city",
        "target_india_aqi_next_day",
        "target_india_aqi_pm_next_day",
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df.isna().any().any():
        raise ValueError("Missing values detected.")

    # Sort by forecast target date
    df = df.sort_values(
        ["target_date", "city"]
    ).reset_index(drop=True)

    # Use common target-date boundaries for all cities
    unique_dates = sorted(df["target_date"].unique())

    total_dates = len(unique_dates)

    train_end = int(total_dates * TRAIN_RATIO)

    validation_end = int(
        total_dates * (TRAIN_RATIO + VALIDATION_RATIO)
    )

    train_dates = unique_dates[:train_end]

    validation_dates = unique_dates[
        train_end:validation_end
    ]

    test_dates = unique_dates[validation_end:]

    # Split records
    train_df = df[
        df["target_date"].isin(train_dates)
    ].copy()

    validation_df = df[
        df["target_date"].isin(validation_dates)
    ].copy()

    test_df = df[
        df["target_date"].isin(test_dates)
    ].copy()

    # Validate chronological separation
    if train_df["target_date"].max() >= validation_df["target_date"].min():
        raise ValueError("Training and validation dates overlap.")

    if validation_df["target_date"].max() >= test_df["target_date"].min():
        raise ValueError("Validation and test dates overlap.")

    # Validate city coverage
    expected_cities = set(df["city"].unique())

    for name, split_df in [
        ("Training", train_df),
        ("Validation", validation_df),
        ("Testing", test_df),
    ]:
        actual_cities = set(split_df["city"].unique())

        if actual_cities != expected_cities:
            raise ValueError(
                f"{name} split does not contain all cities."
            )

    # Save datasets
    train_df.to_csv(
        SPLIT_DIR / "train.csv",
        index=False
    )

    validation_df.to_csv(
        SPLIT_DIR / "validation.csv",
        index=False
    )

    test_df.to_csv(
        SPLIT_DIR / "test.csv",
        index=False
    )

    # Create report
    report = [
        "CHRONOLOGICAL DATA SPLIT REPORT",
        "=" * 55,
        f"Total records: {len(df):,}",
        f"Total unique target dates: {total_dates}",
        f"Total cities: {df['city'].nunique()}",
        "",
        f"Training records: {len(train_df):,}",
        f"Training percentage: {len(train_df) / len(df) * 100:.2f}%",
        f"Training target dates: {train_df['target_date'].min().date()} to {train_df['target_date'].max().date()}",
        "",
        f"Validation records: {len(validation_df):,}",
        f"Validation percentage: {len(validation_df) / len(df) * 100:.2f}%",
        f"Validation target dates: {validation_df['target_date'].min().date()} to {validation_df['target_date'].max().date()}",
        "",
        f"Testing records: {len(test_df):,}",
        f"Testing percentage: {len(test_df) / len(df) * 100:.2f}%",
        f"Testing target dates: {test_df['target_date'].min().date()} to {test_df['target_date'].max().date()}",
        "",
        f"Training missing values: {train_df.isna().sum().sum()}",
        f"Validation missing values: {validation_df.isna().sum().sum()}",
        f"Testing missing values: {test_df.isna().sum().sum()}",
        "",
        "All splits contain all 50 cities.",
        "Target dates are chronologically separated.",
        "No records were randomly shuffled.",
    ]

    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\nDATA SPLITTING COMPLETED")
    print("=" * 45)

    print(f"Total records: {len(df):,}")

    print(
        f"\nTraining: {len(train_df):,} "
        f"({len(train_df) / len(df) * 100:.2f}%)"
    )

    print(
        f"Validation: {len(validation_df):,} "
        f"({len(validation_df) / len(df) * 100:.2f}%)"
    )

    print(
        f"Testing: {len(test_df):,} "
        f"({len(test_df) / len(df) * 100:.2f}%)"
    )

    print(f"\nCities in each split: {df['city'].nunique()}")

    print("\nSaved files:")
    print(SPLIT_DIR / "train.csv")
    print(SPLIT_DIR / "validation.csv")
    print(SPLIT_DIR / "test.csv")
    print(REPORT_FILE)


if __name__ == "__main__":
    main()
