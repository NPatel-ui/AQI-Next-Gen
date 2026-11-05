
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
    print("MODEL PREDICTION FUNCTIONAL TEST")
    print("=" * 65)

    test_df = pd.read_csv(TEST_FILE)

    print(f"\nTest records available: {len(test_df):,}")

    all_passed = True

    for name, config in TARGETS.items():

        print(f"\n{'-' * 65}")
        print(f"Testing: {name}")
        print("-" * 65)

        try:

            model = joblib.load(
                MODEL_DIR / config["model"]
            )

            target = config["target"]

            X = test_df.drop(
                columns=EXCLUDED_COLUMNS,
                errors="ignore"
            )

            y = test_df[target]

            if hasattr(model, "feature_names_in_"):

                expected = list(model.feature_names_in_)

                missing = [
                    col for col in expected
                    if col not in X.columns
                ]

                if missing:
                    raise ValueError(
                        f"Missing model features: {missing}"
                    )

                X = X[expected]

            # Select a small sample for functional testing.
            sample_X = X.head(100)

            predictions = model.predict(sample_X)

            # Basic output validation.
            assert len(predictions) == len(sample_X)
            assert np.isfinite(predictions).all()
            assert np.all(predictions >= 0)
            assert np.all(predictions <= 500)

            # Reproducibility test.
            repeated = model.predict(sample_X)

            assert np.allclose(
                predictions,
                repeated
            )

            print("Feature count:", sample_X.shape[1])
            print("Prediction count:", len(predictions))
            print("Numeric predictions: PASS")
            print("Finite predictions: PASS")
            print("AQI range validation: PASS")
            print("Reproducibility: PASS")

            print(
                "Prediction range:",
                round(float(predictions.min()), 2),
                "to",
                round(float(predictions.max()), 2)
            )

            print(
                "Mean prediction:",
                round(float(predictions.mean()), 2)
            )

            print(
                "Actual mean:",
                round(float(y.head(100).mean()), 2)
            )

            print("RESULT: PASS")

        except Exception as error:

            all_passed = False

            print("RESULT: FAIL")
            print("Error:", error)

    print("\n" + "=" * 65)

    if all_passed:
        print("ALL PREDICTION FUNCTIONAL TESTS PASSED")
    else:
        print("SOME PREDICTION FUNCTIONAL TESTS FAILED")

    print("=" * 65)


if __name__ == "__main__":
    main()
