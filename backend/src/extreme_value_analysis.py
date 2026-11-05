
from pathlib import Path
import pandas as pd
import numpy as np


# PATHS


ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT_DIR / "data" / "raw" / "air_quality_daily.csv"

OUTPUT_DIR = (
    ROOT_DIR / "data" / "reports" / "extreme_value_analysis"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POLLUTANTS = [
    "pm2_5_mean",
    "pm10_mean",
    "no2_mean",
    "so2_mean",
    "o3_8h_max",
    "co_8h_max",
    "dust_mean",
    "aod_mean",
]

TARGETS = ["india_aqi", "india_aqi_pm"]

# Investigation threshold, not an automatic deletion rule.
CITY_PERCENTILE = 0.995


# LOAD DATA


print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"], errors="coerce")

for col in POLLUTANTS + TARGETS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["date", "city"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)

print(f"Records loaded: {len(df):,}")
print(f"Cities: {df['city'].nunique()}")


# 1. GLOBAL AND CITY-SPECIFIC THRESHOLDS


summary_rows = []
extreme_frames = []

for pollutant in POLLUTANTS:

    if pollutant not in df.columns:
        continue

    valid = df.dropna(subset=[pollutant]).copy()

    if valid.empty:
        continue

    global_p99 = valid[pollutant].quantile(0.99)
    global_p995 = valid[pollutant].quantile(0.995)

    city_threshold = (
        valid.groupby("city")[pollutant]
        .transform(lambda x: x.quantile(CITY_PERCENTILE))
    )

    valid["city_threshold"] = city_threshold
    valid["global_p99"] = global_p99
    valid["global_p995"] = global_p995

    # Flag observations above their own city's 99.5th percentile.
    valid["is_extreme"] = (
        valid[pollutant] > valid["city_threshold"]
    )

    extreme = valid[valid["is_extreme"]].copy()

    extreme["pollutant"] = pollutant
    extreme["value"] = extreme[pollutant]

    output_columns = [
        "date",
        "city",
        "pollutant",
        "value",
        "city_threshold",
        "global_p99",
        "global_p995",
        "india_aqi",
        "india_aqi_pm",
    ]

    if "dominant_pollutant" in extreme.columns:
        output_columns.append("dominant_pollutant")

    extreme_frames.append(extreme[output_columns])

    summary_rows.append({
        "pollutant": pollutant,
        "global_p99": global_p99,
        "global_p995": global_p995,
        "extreme_records": len(extreme),
        "extreme_percentage": (
            len(extreme) / len(valid) * 100
        ),
        "maximum": valid[pollutant].max(),
        "cities_affected": extreme["city"].nunique(),
    })

# Save threshold summary
summary_df = pd.DataFrame(summary_rows)

summary_df.to_csv(
    OUTPUT_DIR / "pollutant_threshold_summary.csv",
    index=False
)


# 2. EXTREME RECORDS


if extreme_frames:
    extreme_df = pd.concat(
        extreme_frames,
        ignore_index=True
    )

    extreme_df = extreme_df.sort_values(
        ["pollutant", "city", "date"]
    )

    extreme_df.to_csv(
        OUTPUT_DIR / "extreme_observations.csv",
        index=False
    )
else:
    extreme_df = pd.DataFrame()


# 3. CITY-WISE EXTREME PATTERNS


if not extreme_df.empty:

    city_summary = (
        extreme_df.groupby(["pollutant", "city"])
        .agg(
            extreme_days=("date", "count"),
            maximum_value=("value", "max"),
            average_extreme_value=("value", "mean"),
            first_extreme_date=("date", "min"),
            last_extreme_date=("date", "max"),
        )
        .reset_index()
        .sort_values(
            ["pollutant", "extreme_days"],
            ascending=[True, False]
        )
    )

    city_summary.to_csv(
        OUTPUT_DIR / "city_extreme_patterns.csv",
        index=False
    )


# 4. CONSECUTIVE EXTREME DAYS


run_rows = []

for pollutant in POLLUTANTS:

    if pollutant not in df.columns:
        continue

    for city, group in df.groupby("city"):

        group = group.sort_values("date").copy()

        threshold = group[pollutant].quantile(
            CITY_PERCENTILE
        )

        group["is_extreme"] = (
            group[pollutant] > threshold
        )

        # A new run begins when the extreme flag changes.
        group["run_id"] = (
            group["is_extreme"]
            .ne(group["is_extreme"].shift())
            .cumsum()
        )

        extreme_groups = group[
            group["is_extreme"]
        ].groupby("run_id")

        for _, run in extreme_groups:

            run = run.sort_values("date")

            # Split runs if dates are not consecutive.
            run["date_gap"] = run["date"].diff().dt.days

            run["segment"] = (
                run["date_gap"].ne(1)
            ).cumsum()

            for _, segment in run.groupby("segment"):

                if len(segment) < 2:
                    continue

                run_rows.append({
                    "pollutant": pollutant,
                    "city": city,
                    "start_date": segment["date"].min(),
                    "end_date": segment["date"].max(),
                    "consecutive_days": len(segment),
                    "maximum_value": segment[pollutant].max(),
                    "average_value": segment[pollutant].mean(),
                })

runs_df = pd.DataFrame(run_rows)

runs_df.to_csv(
    OUTPUT_DIR / "consecutive_extreme_events.csv",
    index=False
)


# 5. TARGET VALUES DURING EXTREME OBSERVATIONS


if not extreme_df.empty:

    target_context = (
        extreme_df.groupby("pollutant")
        .agg(
            observations=("value", "count"),
            mean_full_aqi=("india_aqi", "mean"),
            mean_pm_aqi=("india_aqi_pm", "mean"),
            median_full_aqi=("india_aqi", "median"),
            median_pm_aqi=("india_aqi_pm", "median"),
        )
        .reset_index()
    )

    target_context.to_csv(
        OUTPUT_DIR / "extreme_aqi_context.csv",
        index=False
    )


# 6. GENERATE TEXT REPORT


report = []

def section(title):
    report.append("\n" + "=" * 70)
    report.append(title)
    report.append("=" * 70)

section("EXTREME VALUE INVESTIGATION REPORT")

report.append(f"Total records: {len(df):,}")
report.append(f"Cities analysed: {df['city'].nunique()}")
report.append(f"Start date: {df['date'].min().date()}")
report.append(f"End date: {df['date'].max().date()}")
report.append(
    f"City-specific investigation threshold: "
    f"{CITY_PERCENTILE * 100:.1f}th percentile"
)

section("POLLUTANT THRESHOLD SUMMARY")

for _, row in summary_df.iterrows():

    report.append(f"\n{row['pollutant']}")

    report.append(
        f"Global 99th percentile: {row['global_p99']:.3f}"
    )

    report.append(
        f"Global 99.5th percentile: {row['global_p995']:.3f}"
    )

    report.append(
        f"Extreme observations: {row['extreme_records']:,}"
    )

    report.append(
        f"Cities affected: {row['cities_affected']}"
    )

section("CONSECUTIVE EXTREME EVENTS")

if runs_df.empty:
    report.append("No consecutive extreme events found.")
else:
    report.append(
        f"Events lasting at least 2 days: {len(runs_df)}"
    )

    for _, row in runs_df.nlargest(
        20, "consecutive_days"
    ).iterrows():

        report.append(
            f"{row['pollutant']} | {row['city']} | "
            f"{row['start_date'].date()} to "
            f"{row['end_date'].date()} | "
            f"{row['consecutive_days']} days | "
            f"Maximum: {row['maximum_value']:.3f}"
        )

section("IMPORTANT INTERPRETATION")

report.append(
    "These observations are statistical investigation flags, "
    "not confirmed errors."
)

report.append(
    "City-specific thresholds help identify unusual values "
    "relative to each city's own distribution."
)

report.append(
    "No records have been deleted or modified."
)

report.append(
    "Physical validity and measurement units must be checked "
    "against the dataset documentation before filtering."
)

report_path = OUTPUT_DIR / "extreme_value_analysis_report.txt"

with open(report_path, "w", encoding="utf-8") as file:
    file.write("\n".join(report))


# FINISH


print("\n" + "=" * 70)
print("EXTREME VALUE ANALYSIS COMPLETED")
print("=" * 70)

print(f"\nResults saved in: {OUTPUT_DIR}")

for file in sorted(OUTPUT_DIR.iterdir()):
    print(f"- {file.name}")
