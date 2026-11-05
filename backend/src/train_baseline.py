
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)



# PATHS


ROOT = Path(__file__).resolve().parents[1]

SPLIT_DIR = ROOT / "data" / "processed" / "splits"
REPORT_DIR = ROOT / "data" / "reports" / "baseline"

REPORT_DIR.mkdir(parents=True, exist_ok=True)



# TARGET CONFIGURATION


TARGETS = {
    "india_aqi": {
        "current": "india_aqi",
        "future": "target_india_aqi_next_day",
    },
    "india_aqi_pm": {
        "current": "india_aqi_pm",
        "future": "target_india_aqi_pm_next_day",
    },
}

SPLITS = ["train", "validation", "test"]



# METRIC CALCULATION


def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    r2 = r2_score(actual, predicted)

    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    }



# MAIN


def main():

    print("PERSISTENCE BASELINE EVALUATION")
    print("=" * 50)

    results = []

    for split_name in SPLITS:

        print(f"\nLoading {split_name} dataset...")

        file_path = SPLIT_DIR / f"{split_name}.csv"

        df = pd.read_csv(file_path)

        for target_name, columns in TARGETS.items():

            current_col = columns["current"]
            future_col = columns["future"]

            # Persistence prediction:
            # Tomorrow's AQI = Today's AQI

            actual = df[future_col]
            predicted = df[current_col]

            metrics = calculate_metrics(
                actual,
                predicted
            )

            results.append({
                "Target": target_name,
                "Split": split_name,
                "Records": len(df),
                "MAE": metrics["MAE"],
                "RMSE": metrics["RMSE"],
                "R2": metrics["R2"],
            })

            print(f"\nTarget: {target_name}")
            print(f"Records: {len(df):,}")
            print(f"MAE:  {metrics['MAE']:.4f}")
            print(f"RMSE: {metrics['RMSE']:.4f}")
            print(f"R2:   {metrics['R2']:.4f}")

    
    # SAVE RESULTS
    

    results_df = pd.DataFrame(results)

    output_file = REPORT_DIR / "baseline_results.csv"

    results_df.to_csv(
        output_file,
        index=False
    )

    # Human-readable report
    report_file = REPORT_DIR / "baseline_report.txt"

    with open(report_file, "w", encoding="utf-8") as file:

        file.write("PERSISTENCE BASELINE REPORT\n")
        file.write("=" * 60 + "\n\n")

        file.write(
            "Prediction rule: Tomorrow's AQI = Today's AQI\n\n"
        )

        file.write(
            results_df.to_string(index=False, float_format="%.4f")
        )

        file.write("\n\n")

        file.write(
            "This baseline is the benchmark for subsequent "
            "machine learning models.\n"
        )

    print("\n" + "=" * 50)
    print("BASELINE EVALUATION COMPLETED")
    print("=" * 50)

    print("\nResults:")
    print(results_df.to_string(index=False))

    print(f"\nCSV saved: {output_file}")
    print(f"Report saved: {report_file}")


if __name__ == "__main__":
    main()
