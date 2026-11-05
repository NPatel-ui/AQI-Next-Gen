
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)



# PATHS


ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = ROOT / "data" / "reports" / "ml_models"
OUTPUT_DIR = ROOT / "data" / "reports" / "error_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


TARGETS = {
    "india_aqi": {
        "file": "india_aqi_test_predictions.csv",
        "label": "Full India AQI",
    },
    "india_aqi_pm": {
        "file": "india_aqi_pm_test_predictions.csv",
        "label": "PM-based AQI",
    },
}



# AQI CATEGORY CLASSIFICATION
# CPCB India AQI category breakpoints


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



# METRICS


def calculate_metrics(actual, predicted):

    return {
        "MAE": mean_absolute_error(
            actual,
            predicted
        ),

        "RMSE": np.sqrt(
            mean_squared_error(actual, predicted)
        ),

        "R2": r2_score(
            actual,
            predicted
        ),

        "Bias": np.mean(
            predicted - actual
        ),
    }



# PLOT 1: ACTUAL VS PREDICTED


def plot_actual_vs_predicted(df, target, label):

    plt.figure(figsize=(9, 7))

    plt.scatter(
        df["actual"],
        df["predicted"],
        alpha=0.25,
        s=12
    )

    minimum = min(
        df["actual"].min(),
        df["predicted"].min()
    )

    maximum = max(
        df["actual"].max(),
        df["predicted"].max()
    )

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--"
    )

    plt.xlabel("Actual AQI")
    plt.ylabel("Predicted AQI")

    plt.title(
        f"Actual vs Predicted - {label}"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"{target}_actual_vs_predicted.png",
        dpi=150
    )

    plt.close()



# PLOT 2: ERROR DISTRIBUTION


def plot_error_distribution(df, target, label):

    plt.figure(figsize=(9, 6))

    plt.hist(
        df["error"],
        bins=50,
        edgecolor="black"
    )

    plt.axvline(
        0,
        linestyle="--"
    )

    plt.xlabel("Prediction Error (Predicted - Actual)")
    plt.ylabel("Frequency")

    plt.title(
        f"Prediction Error Distribution - {label}"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"{target}_error_distribution.png",
        dpi=150
    )

    plt.close()



# PLOT 3: CITY-WISE MAE


def plot_city_mae(city_metrics, target, label):

    sorted_data = city_metrics.sort_values(
        "MAE",
        ascending=True
    )

    plt.figure(figsize=(11, 12))

    plt.barh(
        sorted_data["city"],
        sorted_data["MAE"]
    )

    plt.xlabel("Mean Absolute Error")
    plt.ylabel("City")

    plt.title(
        f"City-wise Forecasting Error - {label}"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"{target}_city_wise_mae.png",
        dpi=150
    )

    plt.close()



# ANALYZE ONE TARGET


def analyze_target(target, config):

    print("\n" + "=" * 60)
    print(f"ERROR ANALYSIS: {config['label']}")
    print("=" * 60)

    file_path = INPUT_DIR / config["file"]

    df = pd.read_csv(
        file_path,
        parse_dates=[
            "forecast_origin_date",
            "target_date"
        ]
    )

    required = {
        "city",
        "actual",
        "predicted",
        "target_date",
    }

    if not required.issubset(df.columns):
        raise ValueError(
            f"Missing required columns in {file_path}"
        )

    if df[list(required)].isna().any().any():
        raise ValueError(
            "Missing values found in prediction data."
        )

    # Recalculate errors to ensure consistency.
    df["error"] = (
        df["predicted"] - df["actual"]
    )

    df["absolute_error"] = df["error"].abs()

    
    # OVERALL METRICS
    

    overall = calculate_metrics(
        df["actual"],
        df["predicted"]
    )

    print("\nOVERALL TEST PERFORMANCE")

    for metric, value in overall.items():

        print(f"{metric}: {value:.4f}")

    
    # CITY-WISE METRICS
    

    city_rows = []

    for city, group in df.groupby("city"):

        metrics = calculate_metrics(
            group["actual"],
            group["predicted"]
        )

        city_rows.append({
            "city": city,
            "records": len(group),
            **metrics,
        })

    city_metrics = pd.DataFrame(city_rows)

    city_metrics.sort_values(
        "MAE",
        ascending=False,
        inplace=True
    )

    city_metrics.to_csv(
        OUTPUT_DIR / f"{target}_city_metrics.csv",
        index=False
    )

    print("\nTOP 10 CITIES WITH HIGHEST MAE")

    print(
        city_metrics.head(10).to_string(index=False)
    )

    print("\nTOP 10 CITIES WITH LOWEST MAE")

    print(
        city_metrics.tail(10).to_string(index=False)
    )

    
    # AQI CATEGORY PERFORMANCE
    

    df["actual_category"] = df["actual"].apply(
        classify_aqi
    )

    category_rows = []

    for category, group in df.groupby(
        "actual_category",
        observed=True
    ):

        metrics = calculate_metrics(
            group["actual"],
            group["predicted"]
        )

        category_rows.append({
            "actual_category": category,
            "records": len(group),
            **metrics,
        })

    category_metrics = pd.DataFrame(
        category_rows
    )

    category_order = [
        "Good",
        "Satisfactory",
        "Moderate",
        "Poor",
        "Very Poor",
        "Severe",
    ]

    category_metrics["actual_category"] = pd.Categorical(
        category_metrics["actual_category"],
        categories=category_order,
        ordered=True
    )

    category_metrics.sort_values(
        "actual_category",
        inplace=True
    )

    category_metrics.to_csv(
        OUTPUT_DIR / f"{target}_category_metrics.csv",
        index=False
    )

    print("\nAQI CATEGORY PERFORMANCE")

    print(
        category_metrics.to_string(index=False)
    )

    
    # EXTREME AQI PERFORMANCE
    

    extreme_df = df[
        df["actual"] > 300
    ].copy()

    if len(extreme_df) > 0:

        extreme_metrics = calculate_metrics(
            extreme_df["actual"],
            extreme_df["predicted"]
        )

        extreme_summary = pd.DataFrame([{
            "records": len(extreme_df),
            **extreme_metrics,
        }])

    else:

        extreme_summary = pd.DataFrame([{
            "records": 0,
            "MAE": np.nan,
            "RMSE": np.nan,
            "R2": np.nan,
            "Bias": np.nan,
        }])

    extreme_summary.to_csv(
        OUTPUT_DIR / f"{target}_extreme_aqi_metrics.csv",
        index=False
    )

    print("\nEXTREME AQI PERFORMANCE (ACTUAL AQI > 300)")

    print(
        extreme_summary.to_string(index=False)
    )

    
    # LARGEST PREDICTION ERRORS
    

    largest_errors = df.nlargest(
        100,
        "absolute_error"
    )

    largest_errors.to_csv(
        OUTPUT_DIR / f"{target}_largest_errors.csv",
        index=False
    )

    
    # SAVE ALL ANALYZED PREDICTIONS
    

    df.to_csv(
        OUTPUT_DIR / f"{target}_analyzed_predictions.csv",
        index=False
    )

    
    # GENERATE PLOTS
    

    plot_actual_vs_predicted(
        df,
        target,
        config["label"]
    )

    plot_error_distribution(
        df,
        target,
        config["label"]
    )

    plot_city_mae(
        city_metrics,
        target,
        config["label"]
    )

    return {
        "target": target,
        "records": len(df),
        **overall,
        "extreme_records": len(extreme_df),
    }



# MAIN


def main():

    print("AQI FORECASTING ERROR ANALYSIS")
    print("=" * 60)

    summaries = []

    for target, config in TARGETS.items():

        summary = analyze_target(
            target,
            config
        )

        summaries.append(summary)

    summary_df = pd.DataFrame(summaries)

    summary_df.to_csv(
        OUTPUT_DIR / "overall_error_summary.csv",
        index=False
    )

    report_path = (
        OUTPUT_DIR / "error_analysis_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "AQI FORECASTING ERROR ANALYSIS REPORT\n"
        )

        file.write("=" * 60 + "\n\n")

        file.write(
            summary_df.to_string(
                index=False,
                float_format="%.4f"
            )
        )

        file.write("\n")

    print("\n" + "=" * 60)
    print("ERROR ANALYSIS COMPLETED")
    print("=" * 60)

    print(
        summary_df.to_string(index=False)
    )

    print(f"\nAll reports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
