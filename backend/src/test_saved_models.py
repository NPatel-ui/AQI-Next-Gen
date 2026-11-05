
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = ROOT / "models" / "initial_models"

MODEL_FILES = {
    "Full India AQI": "india_aqi_best_model.joblib",
    "PM-based AQI": "india_aqi_pm_best_model.joblib",
}

print("=" * 65)
print("SAVED MODEL LOADING TEST")
print("=" * 65)

all_passed = True

for model_name, filename in MODEL_FILES.items():

    model_path = MODEL_DIR / filename

    print(f"\nTesting: {model_name}")

    try:
        if not model_path.exists():
            raise FileNotFoundError(model_path)

        model = joblib.load(model_path)

        print("Status: PASS")
        print("Model class:", type(model).__name__)

        if hasattr(model, "n_features_in_"):
            print("Expected input features:", model.n_features_in_)

        if hasattr(model, "feature_names_in_"):
            print("Feature names available:", len(model.feature_names_in_))

        print("Model loaded successfully.")

    except Exception as error:
        all_passed = False
        print("Status: FAIL")
        print("Error:", error)

print("\n" + "=" * 65)

if all_passed:
    print("RESULT: ALL MODEL LOADING TESTS PASSED")
else:
    print("RESULT: SOME MODEL LOADING TESTS FAILED")

print("=" * 65)
