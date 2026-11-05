
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


ROOT = Path(__file__).resolve().parents[1]

TEST_FILE = ROOT / "data" / "processed" / "splits" / "test.csv"
MODEL_DIR = ROOT / "models" / "initial_models"

OUTPUT_DIR = (
    ROOT / "data" / "reports" / "test_evaluation"
)

TARGETS = {
    "Full India AQI": {
        "model": "india_aqi_best_model.joblib",
        "target": "target_india_aqi_next_day",
    },
    "PM-based AQI": {
        "model": "india_aqi_pm_best_model.joblib",
        "target": "target_india_aqi_pm_next_day",
    },
}

EXCLUDED_COLUMNS = [
    "date",
    "target_date",
    "target_india_aqi_next_day",
    "target_india_aqi_pm_next_day",
    "state",
    "region",
]


def main():

    print("=" * 65)
    print("FINAL TEST DATASET EVALUATION")
    print("=" * 65)

    df = pd.read_csv(TEST_FILE)

    print("\nTest dataset records:", len(df))
    print("Cities:", df["city"].nunique())

    X = df.drop(
        columns=EXCLUDED_COLUMNS,
        errors="ignore"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    summary = []

    for name, config in TARGETS.items():

        print("\n" + "-" * 65)
        print("Evaluating:", name)
        print("-" * 65)

        model_path = MODEL_DIR / config["model"]

        model = joblib.load(model_path)

        expected_features = list(
            model.feature_names_in_
        )

        X_model = X[expected_features]

        y_actual = df[config["target"]].values

        # Generate raw model predictions.
        y_pred = model.predict(X_model)

        # Do not clip predictions for historical
        # model evaluation. Preserve original metrics.
        assert np.isfinite(y_pred).all()

        mae = mean_absolute_error(
            y_actual,
            y_pred
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_actual,
                y_pred
            )
        )

        r2 = r2_score(
            y_actual,
            y_pred
        )

        print("Records evaluated:", len(y_pred))
        print(f"MAE:  {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2:   {r2:.4f}")

        print(
            "Predictions below 0:",
            int((y_pred < 0).sum())
        )

        print(
            "Predictions above 500:",
            int((y_pred > 500).sum())
        )

        predictions_df = pd.DataFrame({
            "city": df["city"],
            "target_date": df["target_date"],
            "actual": y_actual,
            "predicted": y_pred,
            "absolute_error": np.abs(y_actual - y_pred),
        })

        filename = (
            "full_aqi_test_predictions.csv"
            if name == "Full India AQI"
            else "pm_aqi_test_predictions.csv"
        )

        predictions_df.to_csv(
            OUTPUT_DIR / filename,
            index=False
        )

        summary.append({
            "Model": name,
            "Records": len(y_pred),
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
        })

    summary_df = pd.DataFrame(summary)

    summary_df.to_csv(
        OUTPUT_DIR / "test_metrics_summary.csv",
        index=False
    )

    print("\n" + "=" * 65)
    print("FINAL TEST RESULTS")
    print("=" * 65)

    print(
        summary_df.round(4).to_string(index=False)
    )

    print("\nEvaluation reports saved to:")
    print(OUTPUT_DIR)

    print("\nTEST DATASET EVALUATION COMPLETED")


if __name__ == "__main__":
    main()
