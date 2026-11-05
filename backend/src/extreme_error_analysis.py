
from pathlib import Path

import numpy as np
import pandas as pd



# PATHS


ROOT = Path(__file__).resolve().parents[1]

SPLIT_DIR = ROOT / "data" / "processed" / "splits"
PREDICTION_DIR = ROOT / "data" / "reports" / "ml_models"

OUTPUT_DIR = ROOT / "data" / "reports" / "extreme_error_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



# TARGET CONFIGURATION


TARGETS = {
    "india_aqi": {
        "prediction_file": "india_aqi_test_predictions.csv",
        "target_column": "target_india_aqi_next_day",
        "label": "Full India AQI",
    },
    "india_aqi_pm": {
        "prediction_file": "india_aqi_pm_test_predictions.csv",
        "target_column": "target_india_aqi_pm_next_day",
        "label": "PM-based AQI",
    },
}

SPLITS = ["train", "validation", "test"]

THRESHOLDS = [200, 300, 400]



# HELPER FUNCTIONS


def calculate_error_metrics(df):

    actual = df["actual"]
    predicted = df["predicted"]

    error = predicted - actual

    return {
        "records": len(df),
        "MAE": np.mean(np.abs(error)),
        "RMSE": np.sqrt(np.mean(error ** 2)),
        "Bias": np.mean(error),
        "Underprediction_rate_pct": (
            (error < 0).mean() * 100
        ),
        "Overprediction_rate_pct": (
            (error > 0).mean() * 100
        ),
    }


def classify_aqi(value):

    if value <= 50:
        return "Good"
    elif value <= 100:
        return "Satisfactory"
    elif value <= 200:
        return "Moderate"
    elif value <= 300:
        return "Poor"
    elif value <= 400:
        return "Very Poor"
    else:
        return "Severe"


def save_csv(data, filename):

    pd.DataFrame(data).to_csv(
        OUTPUT_DIR / filename,
        index=False
    )



# 1. TARGET DISTRIBUTION ACROSS SPLITS


def analyze_target_distribution(target, config):

    print("\nTARGET DISTRIBUTION ANALYSIS")

    rows = []

    for split in SPLITS:

        df = pd.read_csv(
            SPLIT_DIR / f"{split}.csv",
            usecols=[
                "target_date",
                config["target_column"]
            ],
            parse_dates=["target_date"]
        )

        actual = df[config["target_column"]]

        row = {
            "target": target,
            "split": split,
            "records": len(df),
            "mean": actual.mean(),
            "median": actual.median(),
            "std": actual.std(),
            "maximum": actual.max(),
        }

        for threshold in THRESHOLDS:

            count = (actual > threshold).sum()

            row[f"count_above_{threshold}"] = count

            row[f"percentage_above_{threshold}"] = (
                count / len(df) * 100
            )

        rows.append(row)

    result = pd.DataFrame(rows)

    result.to_csv(
        OUTPUT_DIR / f"{target}_split_distribution.csv",
        index=False
    )

    print(result.to_string(index=False))

    return result



# 2. EXTREME THRESHOLD PERFORMANCE


def analyze_threshold_errors(df, target):

    rows = []

    for threshold in THRESHOLDS:

        subset = df[
            df["actual"] > threshold
        ].copy()

        if subset.empty:
            continue

        metrics = calculate_error_metrics(subset)

        # Magnitude of underprediction only
        underprediction = (
            subset["actual"] - subset["predicted"]
        ).clip(lower=0)

        metrics.update({
            "target": target,
            "actual_threshold": threshold,
            "mean_underprediction_magnitude": (
                underprediction.mean()
            ),
            "median_underprediction_magnitude": (
                underprediction.median()
            ),
        })

        rows.append(metrics)

    result = pd.DataFrame(rows)

    result.to_csv(
        OUTPUT_DIR / f"{target}_threshold_errors.csv",
        index=False
    )

    print("\nERRORS AT DIFFERENT AQI THRESHOLDS")
    print(result.to_string(index=False))

    return result



# 3. EXTREME CITY PERFORMANCE


def analyze_city_extremes(df, target):

    rows = []

    for city, group in df.groupby("city"):

        for threshold in THRESHOLDS:

            subset = group[
                group["actual"] > threshold
            ]

            if subset.empty:
                continue

            metrics = calculate_error_metrics(subset)

            rows.append({
                "city": city,
                "target": target,
                "actual_threshold": threshold,
                **metrics,
            })

    result = pd.DataFrame(rows)

    result.to_csv(
        OUTPUT_DIR / f"{target}_city_extreme_errors.csv",
        index=False
    )

    print("\nWORST CITIES FOR ACTUAL AQI ABOVE 300")

    if not result.empty:

        worst = result[
            result["actual_threshold"] == 300
        ].sort_values(
            "MAE",
            ascending=False
        ).head(15)

        print(worst.to_string(index=False))

    return result



# 4. MONTHLY EXTREME PERFORMANCE


def analyze_monthly_extremes(df, target):

    df = df.copy()

    df["month"] = (
        df["target_date"].dt.month
    )

    df["month_name"] = (
        df["target_date"].dt.strftime("%B")
    )

    rows = []

    for month, group in df.groupby("month"):

        for threshold in THRESHOLDS:

            subset = group[
                group["actual"] > threshold
            ]

            if subset.empty:
                continue

            metrics = calculate_error_metrics(subset)

            rows.append({
                "month": month,
                "month_name": subset["month_name"].iloc[0],
                "target": target,
                "actual_threshold": threshold,
                **metrics,
            })

    result = pd.DataFrame(rows)

    result.to_csv(
        OUTPUT_DIR / f"{target}_monthly_extreme_errors.csv",
        index=False
    )

    return result



# 5. EXTREME UNDERPREDICTION EXAMPLES


def save_worst_predictions(df, target):

    df = df.copy()

    df["error"] = (
        df["predicted"] - df["actual"]
    )

    df["absolute_error"] = df["error"].abs()

    df["actual_category"] = (
        df["actual"].apply(classify_aqi)
    )

    # Largest underpredictions
    underpredictions = df[
        df["error"] < 0
    ].sort_values(
        "error",
        ascending=True
    ).head(200)

    underpredictions.to_csv(
        OUTPUT_DIR / f"{target}_worst_underpredictions.csv",
        index=False
    )

    # Largest absolute errors
    largest_errors = df.nlargest(
        200,
        "absolute_error"
    )

    largest_errors.to_csv(
        OUTPUT_DIR / f"{target}_largest_extreme_errors.csv",
        index=False
    )



# 6. TARGET RANGE ANALYSIS


def analyze_prediction_ranges(df, target):

    df = df.copy()

    bins = [
        0, 50, 100, 200, 300, 400, np.inf
    ]

    labels = [
        "0-50",
        "51-100",
        "101-200",
        "201-300",
        "301-400",
        "Above 400",
    ]

    df["actual_range"] = pd.cut(
        df["actual"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    rows = []

    for range_name, group in df.groupby(
        "actual_range",
        observed=False
    ):

        if group.empty:
            continue

        metrics = calculate_error_metrics(group)

        rows.append({
            "target": target,
            "actual_range": str(range_name),
            **metrics,
        })

    result = pd.DataFrame(rows)

    result.to_csv(
        OUTPUT_DIR / f"{target}_prediction_ranges.csv",
        index=False
    )

    print("\nPREDICTION RANGE ANALYSIS")
    print(result.to_string(index=False))

    return result



# 7. PROCESS ONE TARGET


def analyze_target(target, config):

    print("\n" + "=" * 65)
    print(f"ADVANCED EXTREME ANALYSIS: {config['label']}")
    print("=" * 65)

    prediction_file = (
        PREDICTION_DIR / config["prediction_file"]
    )

    df = pd.read_csv(
        prediction_file,
        parse_dates=[
            "forecast_origin_date",
            "target_date"
        ]
    )

    required = [
        "city",
        "target_date",
        "actual",
        "predicted",
    ]

    if df[required].isna().any().any():
        raise ValueError(
            f"Missing values found in {target} predictions."
        )

    if len(df) != 11600:
        raise ValueError(
            f"Unexpected test record count for {target}: {len(df)}"
        )

    # Validate target dates and prediction range
    if not (
        df["target_date"] - df["forecast_origin_date"]
    ).dt.days.eq(1).all():
        raise ValueError(
            "Prediction dates are not exactly one day apart."
        )

    if (df["actual"] < 0).any():
        raise ValueError("Negative actual AQI values found.")

    
    # ANALYSES
    

    distribution = analyze_target_distribution(
        target,
        config
    )

    threshold_errors = analyze_threshold_errors(
        df,
        target
    )

    city_errors = analyze_city_extremes(
        df,
        target
    )

    monthly_errors = analyze_monthly_extremes(
        df,
        target
    )

    range_errors = analyze_prediction_ranges(
        df,
        target
    )

    save_worst_predictions(
        df,
        target
    )

    return {
        "target": target,
        "test_records": len(df),
        "overall_mae": np.mean(
            np.abs(df["predicted"] - df["actual"])
        ),
        "overall_bias": np.mean(
            df["predicted"] - df["actual"]
        ),
        "records_above_300": int(
            (df["actual"] > 300).sum()
        ),
        "extreme_mae_above_300": (
            threshold_errors.loc[
                threshold_errors["actual_threshold"] == 300,
                "MAE"
            ].iloc[0]
            if 300 in threshold_errors["actual_threshold"].values
            else np.nan
        ),
    }



# MAIN


def main():

    print("ADVANCED AQI EXTREME ERROR ANALYSIS")
    print("=" * 65)

    summaries = []

    for target, config in TARGETS.items():

        summary = analyze_target(
            target,
            config
        )

        summaries.append(summary)

    summary_df = pd.DataFrame(summaries)

    summary_df.to_csv(
        OUTPUT_DIR / "extreme_analysis_summary.csv",
        index=False
    )

    report_path = (
        OUTPUT_DIR / "extreme_analysis_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "ADVANCED AQI EXTREME ERROR ANALYSIS\n"
        )

        file.write("=" * 65 + "\n\n")

        file.write(
            summary_df.to_string(
                index=False,
                float_format="%.4f"
            )
        )

        file.write("\n\n")

        file.write(
            "Threshold definition: actual AQI > 200, > 300, > 400.\n"
        )

        file.write(
            "Underprediction rate measures the percentage of "
            "observations where predicted AQI is below actual AQI.\n"
        )

    print("\n" + "=" * 65)
    print("ADVANCED EXTREME ANALYSIS COMPLETED")
    print("=" * 65)

    print(summary_df.to_string(index=False))

    print(f"\nReports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
