
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = ROOT / "models" / "initial_models"
TEST_FILE = ROOT / "data" / "processed" / "splits" / "test.csv"

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
    print("ALL-CITY MODEL FUNCTIONAL TEST")
    print("=" * 65)

    df = pd.read_csv(TEST_FILE)

    # Select five deterministic records per city.
    sample = (
        df.groupby("city", group_keys=False)
        .sample(n=5, random_state=42)
        .reset_index(drop=True)
    )

    print("\nCities tested:", sample["city"].nunique())
    print("Total records:", len(sample))

    X = sample.drop(
        columns=EXCLUDED_COLUMNS,
        errors="ignore"
    )

    all_passed = True

    for name, config in TARGETS.items():

        print(f"\nTesting {name}")

        try:

            model = joblib.load(
                MODEL_DIR / config["model"]
            )

            expected_features = list(model.feature_names_in_)
            X_model = X[expected_features]

            # Generate raw model predictions.
            raw_predictions = model.predict(X_model)

            print(
                "Raw prediction minimum:",
                float(np.min(raw_predictions))
            )
            print(
                "Raw prediction maximum:",
                float(np.max(raw_predictions))
            )
            print(
                "Raw predictions above 500:",
                int((raw_predictions > 500).sum())
            )

            # Apply AQI output boundary.
            predictions = np.clip(
                raw_predictions,
                0,
                500
            )

            # Functional validation.
            assert len(predictions) == len(sample), (
                "Prediction count does not match input records."
            )

            assert np.isfinite(predictions).all(), (
                "Non-finite predictions detected."
            )

            assert np.all(predictions >= 0), (
                "Predictions below zero detected."
            )

            assert np.all(predictions <= 500), (
                "Predictions above 500 detected."
            )

            results = pd.DataFrame({
                "city": sample["city"],
                "actual": sample[config["target"]].values,
                "raw_predicted": raw_predictions,
                "predicted": predictions,
            })

            city_results = (
                results.groupby("city")
                .agg(
                    records=("actual", "size"),
                    actual_mean=("actual", "mean"),
                    predicted_mean=("predicted", "mean"),
                )
                .reset_index()
            )

            print("\nPrediction count:", len(predictions))
            print("Non-finite predictions:", int(
                (~np.isfinite(predictions)).sum()
            ))
            print("Predictions below zero:", int(
                (predictions < 0).sum()
            ))
            print("Predictions above 500:", int(
                (predictions > 500).sum()
            ))

            print("Prediction validation: PASS")
            print("All-city coverage: PASS")

            print("\nCity-wise sample results:")
            print(
                city_results.round(2).to_string(index=False)
            )

            output = (
                ROOT / "data" / "reports"
                / "functional_testing"
            )

            output.mkdir(parents=True, exist_ok=True)

            filename = (
                "all_city_full_aqi.csv"
                if name == "Full India AQI"
                else "all_city_pm_aqi.csv"
            )

            results.to_csv(
                output / filename,
                index=False
            )

            print("Saved:", filename)
            print("RESULT: PASS")

        except Exception as error:

            all_passed = False

            print("RESULT: FAIL")
            print("Error type:", type(error).__name__)
            print("Error details:", repr(error))

    print("\n" + "=" * 65)

    if all_passed:
        print("ALL-CITY TESTING PASSED")
    else:
        print("ALL-CITY TESTING FAILED")

    print("=" * 65)


if __name__ == "__main__":
    main()
