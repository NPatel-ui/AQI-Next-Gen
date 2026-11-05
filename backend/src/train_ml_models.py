
from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler



# PATHS


ROOT = Path(__file__).resolve().parents[1]

SPLIT_DIR = ROOT / "data" / "processed" / "splits"
MODEL_DIR = ROOT / "models" / "initial_models"
REPORT_DIR = ROOT / "data" / "reports" / "ml_models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)



# CONFIGURATION


TARGETS = {
    "india_aqi": "target_india_aqi_next_day",
    "india_aqi_pm": "target_india_aqi_pm_next_day",
}

EXCLUDED_COLUMNS = [
    "date",
    "target_date",
    "target_india_aqi_next_day",
    "target_india_aqi_pm_next_day",
    "state",
    "region",
]

RANDOM_STATE = 42



# METRICS


def calculate_metrics(actual, predicted):

    return {
        "MAE": float(
            mean_absolute_error(actual, predicted)
        ),
        "RMSE": float(
            np.sqrt(mean_squared_error(actual, predicted))
        ),
        "R2": float(
            r2_score(actual, predicted)
        ),
    }



# ENCODER COMPATIBILITY


def create_one_hot_encoder():

    try:
        return OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )

    except TypeError:
        return OneHotEncoder(
            handle_unknown="ignore",
            sparse=False
        )



# MODEL DEFINITIONS


def get_models():

    return {
        "LinearRegression": LinearRegression(),

        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features=0.8,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),

        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.08,
            max_leaf_nodes=31,
            l2_regularization=1.0,
            random_state=RANDOM_STATE,
        ),
    }

def load_datasets():

    train = pd.read_csv(
        SPLIT_DIR / "train.csv"
    )

    validation = pd.read_csv(
        SPLIT_DIR / "validation.csv"
    )

    test = pd.read_csv(
        SPLIT_DIR / "test.csv"
    )

    return train, validation, test


def prepare_features(train, validation, test):

    excluded = set(EXCLUDED_COLUMNS)

    feature_columns = [
        col for col in train.columns
        if col not in excluded
    ]

    # City is the only categorical predictor.
    categorical_columns = ["city"]

    if "city" not in feature_columns:
        raise ValueError("City column is missing.")

    numeric_columns = [
        col for col in feature_columns
        if col not in categorical_columns
    ]

    # Check that all remaining features are numeric.
    non_numeric = [
        col for col in numeric_columns
        if not pd.api.types.is_numeric_dtype(train[col])
    ]

    if non_numeric:
        raise ValueError(
            f"Unexpected non-numeric features: {non_numeric}"
        )

    X_train = train[feature_columns].copy()
    X_validation = validation[feature_columns].copy()
    X_test = test[feature_columns].copy()

    # Validate that feature columns match.
    assert list(X_train.columns) == list(X_validation.columns)
    assert list(X_train.columns) == list(X_test.columns)

    return (
        X_train,
        X_validation,
        X_test,
        numeric_columns,
        categorical_columns,
    )




def create_preprocessor(
    numeric_columns,
    categorical_columns,
    scale_numeric=False
):

    numeric_steps = [
        ("imputer", SimpleImputer(strategy="median"))
    ]

    if scale_numeric:
        numeric_steps.append(
            ("scaler", StandardScaler())
        )

    numeric_pipeline = Pipeline(
        steps=numeric_steps
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "encoder",
                create_one_hot_encoder()
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                numeric_columns
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_columns
            ),
        ],
        remainder="drop",
    )




def main():

    warnings.filterwarnings(
        "ignore",
        category=FutureWarning
    )

    print("=" * 65)
    print("AQI MACHINE LEARNING MODEL COMPARISON")
    print("=" * 65)

    train, validation, test = load_datasets()

    print(f"\nTraining records: {len(train):,}")
    print(f"Validation records: {len(validation):,}")
    print(f"Testing records: {len(test):,}")

    (
        X_train,
        X_validation,
        X_test,
        numeric_columns,
        categorical_columns,
    ) = prepare_features(
        train,
        validation,
        test
    )

    print(f"\nNumeric features: {len(numeric_columns)}")
    print(f"Categorical features: {len(categorical_columns)}")
    print(f"Total input features: {X_train.shape[1]}")

    all_results = []
    selected_models = {}


    for target_name, target_column in TARGETS.items():

        print("\n" + "=" * 65)
        print(f"TARGET: {target_name}")
        print("=" * 65)

        y_train = train[target_column]
        y_validation = validation[target_column]
        y_test = test[target_column]

        models = get_models()

        validation_results = []

        for model_name, estimator in models.items():

            print(f"\nTraining {model_name}...")

            # Scale numerical inputs for Linear Regression.
            scale_numeric = (
                model_name == "LinearRegression"
            )

            preprocessor = create_preprocessor(
                numeric_columns,
                categorical_columns,
                scale_numeric=scale_numeric
            )

            pipeline = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("model", estimator),
                ]
            )

            pipeline.fit(
                X_train,
                y_train
            )

            # Training performance
            train_predictions = pipeline.predict(
                X_train
            )

            train_metrics = calculate_metrics(
                y_train,
                train_predictions
            )

            # Validation performance
            validation_predictions = pipeline.predict(
                X_validation
            )

            validation_metrics = calculate_metrics(
                y_validation,
                validation_predictions
            )

            print(
                f"Train MAE: {train_metrics['MAE']:.4f}"
            )

            print(
                f"Validation MAE: "
                f"{validation_metrics['MAE']:.4f}"
            )

            print(
                f"Validation RMSE: "
                f"{validation_metrics['RMSE']:.4f}"
            )

            print(
                f"Validation R2: "
                f"{validation_metrics['R2']:.4f}"
            )

            result = {
                "Target": target_name,
                "Model": model_name,

                "Train_MAE": train_metrics["MAE"],
                "Train_RMSE": train_metrics["RMSE"],
                "Train_R2": train_metrics["R2"],

                "Validation_MAE": validation_metrics["MAE"],
                "Validation_RMSE": validation_metrics["RMSE"],
                "Validation_R2": validation_metrics["R2"],
            }

            all_results.append(result)

            validation_results.append({
                "model_name": model_name,
                "pipeline": pipeline,
                "validation_mae": validation_metrics["MAE"],
            })

        
        validation_results.sort(
            key=lambda x: x["validation_mae"]
        )

        best = validation_results[0]

        best_model = best["pipeline"]

        print("\nBEST MODEL SELECTED")
        print(f"Model: {best['model_name']}")
        print(
            f"Validation MAE: "
            f"{best['validation_mae']:.4f}"
        )

       
        print("\nEvaluating selected model on test data...")

        test_predictions = best_model.predict(
            X_test
        )

        test_metrics = calculate_metrics(
            y_test,
            test_predictions
        )

        print(f"Test MAE: {test_metrics['MAE']:.4f}")
        print(f"Test RMSE: {test_metrics['RMSE']:.4f}")
        print(f"Test R2: {test_metrics['R2']:.4f}")

        # Save selected model
        model_path = (
            MODEL_DIR / f"{target_name}_best_model.joblib"
        )

        joblib.dump(
            best_model,
            model_path
        )

        # Save test predictions
        prediction_df = pd.DataFrame({
            "city": test["city"],
            "forecast_origin_date": test["date"],
            "target_date": test["target_date"],
            "actual": y_test,
            "predicted": test_predictions,
            "absolute_error": np.abs(
                y_test.to_numpy() - test_predictions
            ),
        })

        prediction_df.to_csv(
            REPORT_DIR / f"{target_name}_test_predictions.csv",
            index=False
        )

        selected_models[target_name] = {
            "best_model": best["model_name"],
            "validation_mae": best["validation_mae"],
            "test_metrics": test_metrics,
            "model_path": str(model_path),
        }

    

    results_df = pd.DataFrame(all_results)

    results_df.to_csv(
        REPORT_DIR / "model_comparison.csv",
        index=False
    )

    with open(
        REPORT_DIR / "selected_models.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            selected_models,
            file,
            indent=4
        )

    print("\n" + "=" * 65)
    print("MODEL COMPARISON COMPLETED")
    print("=" * 65)

    print("\nValidation comparison:")

    print(
        results_df[
            [
                "Target",
                "Model",
                "Validation_MAE",
                "Validation_RMSE",
                "Validation_R2",
            ]
        ].sort_values(
            ["Target", "Validation_MAE"]
        ).to_string(index=False)
    )

    print("\nSelected models and test results:")

    for target, details in selected_models.items():

        print(f"\n{target}")
        print(f"Best model: {details['best_model']}")
        print(
            f"Test MAE: "
            f"{details['test_metrics']['MAE']:.4f}"
        )
        print(
            f"Test RMSE: "
            f"{details['test_metrics']['RMSE']:.4f}"
        )
        print(
            f"Test R2: "
            f"{details['test_metrics']['R2']:.4f}"
        )

    print("\nSaved outputs:")
    print(MODEL_DIR)
    print(REPORT_DIR)


if __name__ == "__main__":
    main()
