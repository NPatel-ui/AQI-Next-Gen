
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# PATHS AND CONFIGURATION


ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT_DIR / "data" / "raw" / "air_quality_daily.csv"
OUTPUT_DIR = ROOT_DIR / "data" / "reports" / "target_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

TARGETS = ["india_aqi", "india_aqi_pm"]

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


# LOAD DATA


print("\nLoading dataset...")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"], errors="coerce")

for column in TARGETS + POLLUTANTS:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=["date", "city"])

df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year
df["season"] = df["month"].map({
    12: "Winter",
    1: "Winter",
    2: "Winter",
    3: "Summer",
    4: "Summer",
    5: "Summer",
    6: "Monsoon",
    7: "Monsoon",
    8: "Monsoon",
    9: "Monsoon",
    10: "Post-Monsoon",
    11: "Post-Monsoon",
})

report = []

def section(title):
    report.append("\n" + "=" * 75)
    report.append(title)
    report.append("=" * 75)

def line(label, value):
    report.append(f"{label:<42}: {value}")


# 1. TARGET COMPARISON


section("1. AQI TARGET COMPARISON")

target_stats = []

for target in TARGETS:
    if target not in df.columns:
        continue

    values = df[target].dropna()

    stats = {
        "target": target,
        "count": len(values),
        "mean": values.mean(),
        "median": values.median(),
        "std": values.std(),
        "min": values.min(),
        "max": values.max(),
        "p95": values.quantile(0.95),
        "p99": values.quantile(0.99),
    }

    target_stats.append(stats)

    report.append(f"\n{target}")

    for key, value in stats.items():
        if key != "target":
            line(key, round(value, 3))

pd.DataFrame(target_stats).to_csv(
    OUTPUT_DIR / "target_statistics.csv",
    index=False
)


# 2. CITY-WISE AQI ANALYSIS


section("2. CITY-WISE AQI ANALYSIS")

city_stats = (
    df.groupby("city")
    .agg(
        records=("date", "count"),
        india_aqi_mean=("india_aqi", "mean"),
        india_aqi_median=("india_aqi", "median"),
        india_aqi_pm_mean=("india_aqi_pm", "mean"),
        india_aqi_pm_median=("india_aqi_pm", "median"),
    )
    .reset_index()
)

city_stats = city_stats.sort_values(
    "india_aqi_mean",
    ascending=False
)

city_stats.to_csv(
    OUTPUT_DIR / "city_aqi_statistics.csv",
    index=False
)

report.append("\nHighest average AQI cities:")

for _, row in city_stats.head(10).iterrows():
    report.append(
        f"{row['city']:<25} "
        f"Full AQI: {row['india_aqi_mean']:.2f} | "
        f"PM AQI: {row['india_aqi_pm_mean']:.2f}"
    )

report.append("\nLowest average AQI cities:")

for _, row in city_stats.tail(10).iterrows():
    report.append(
        f"{row['city']:<25} "
        f"Full AQI: {row['india_aqi_mean']:.2f} | "
        f"PM AQI: {row['india_aqi_pm_mean']:.2f}"
    )


# 3. POLLUTANT CORRELATION


section("3. POLLUTANT AND AQI CORRELATION")

correlation_columns = [
    column
    for column in TARGETS + POLLUTANTS
    if column in df.columns
]

correlation = df[correlation_columns].corr(method="pearson")

correlation.to_csv(
    OUTPUT_DIR / "correlation_matrix.csv"
)

report.append("\nCorrelation with AQI targets:")

for target in TARGETS:
    if target not in correlation.columns:
        continue

    report.append(f"\nTarget: {target}")

    values = correlation[target].drop(
        labels=TARGETS,
        errors="ignore"
    ).sort_values(ascending=False)

    for pollutant, value in values.items():
        report.append(
            f"{pollutant:<25}: {value:.4f}"
        )

plt.figure(figsize=(13, 10))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True
)

plt.title("AQI and Pollutant Correlation Matrix")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "correlation_heatmap.png",
    dpi=200
)

plt.close()


# 4. OZONE DOMINANCE ANALYSIS


section("4. OZONE DOMINANCE ANALYSIS")

if "dominant_pollutant" in df.columns:

    dominant = df["dominant_pollutant"].value_counts(
        normalize=True
    ) * 100

    report.append("\nDominant pollutant percentages:")

    for pollutant, percentage in dominant.items():
        report.append(
            f"{str(pollutant):<25}: {percentage:.2f}%"
        )

    if "O3" in dominant.index:
        line(
            "Ozone dominant percentage",
            f"{dominant['O3']:.2f}%"
        )


# 5. EXTREME VALUE INVESTIGATION


section("5. EXTREME POLLUTANT VALUE INVESTIGATION")

extreme_rows = []

for pollutant in POLLUTANTS:

    if pollutant not in df.columns:
        continue

    values = df[pollutant].dropna()

    if values.empty:
        continue

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 3 * iqr
    upper_bound = q3 + 3 * iqr

    outliers = df[
        (df[pollutant] < lower_bound)
        | (df[pollutant] > upper_bound)
    ].copy()

    extreme_rows.append({
        "pollutant": pollutant,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": len(outliers),
        "outlier_percentage": len(outliers) / len(df) * 100,
        "maximum": values.max(),
    })

    report.append(f"\n{pollutant}")

    line("Maximum", round(values.max(), 3))
    line("Upper investigation threshold", round(upper_bound, 3))
    line("Potential extreme records", len(outliers))

    outliers = outliers.sort_values(
        pollutant,
        ascending=False
    )

    for _, row in outliers.head(10).iterrows():
        report.append(
            f"  {row['date'].date()} | "
            f"{row['city']} | "
            f"{pollutant}={row[pollutant]:.3f}"
        )

pd.DataFrame(extreme_rows).to_csv(
    OUTPUT_DIR / "extreme_value_summary.csv",
    index=False
)

# Save the 100 highest values per pollutant for investigation.
extreme_detail_frames = []

for pollutant in POLLUTANTS:

    if pollutant not in df.columns:
        continue

    top = df.nlargest(100, pollutant)[
        ["date", "city", pollutant]
    ].copy()

    top["pollutant"] = pollutant
    top = top.rename(columns={pollutant: "value"})

    extreme_detail_frames.append(top)

if extreme_detail_frames:
    pd.concat(
        extreme_detail_frames,
        ignore_index=True
    ).to_csv(
        OUTPUT_DIR / "extreme_value_records.csv",
        index=False
    )


# 6. SEASONAL AQI ANALYSIS


section("6. SEASONAL AQI ANALYSIS")

seasonal = (
    df.groupby("season")
    .agg(
        india_aqi_mean=("india_aqi", "mean"),
        india_aqi_pm_mean=("india_aqi_pm", "mean"),
        records=("date", "count")
    )
    .reset_index()
)

seasonal.to_csv(
    OUTPUT_DIR / "seasonal_aqi_statistics.csv",
    index=False
)

report.append("\nSeasonal averages:")

for _, row in seasonal.iterrows():
    report.append(
        f"{row['season']:<20} "
        f"Full AQI: {row['india_aqi_mean']:.2f} | "
        f"PM AQI: {row['india_aqi_pm_mean']:.2f}"
    )


# 7. MONTHLY AQI ANALYSIS


section("7. MONTHLY AQI ANALYSIS")

monthly = (
    df.groupby("month")
    .agg(
        india_aqi_mean=("india_aqi", "mean"),
        india_aqi_pm_mean=("india_aqi_pm", "mean")
    )
    .reset_index()
)

monthly.to_csv(
    OUTPUT_DIR / "monthly_aqi_statistics.csv",
    index=False
)

plt.figure(figsize=(12, 6))

plt.plot(
    monthly["month"],
    monthly["india_aqi_mean"],
    marker="o",
    label="Full India AQI"
)

plt.plot(
    monthly["month"],
    monthly["india_aqi_pm_mean"],
    marker="o",
    label="PM-based India AQI"
)

plt.xticks(range(1, 13))

plt.xlabel("Month")
plt.ylabel("Average AQI")
plt.title("Monthly AQI Patterns")
plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "monthly_aqi_patterns.png",
    dpi=200
)

plt.close()


# 8. CITY-WISE TARGET RELATIONSHIP


section("8. RELATIONSHIP BETWEEN AQI TARGETS")

target_relationship = df[
    ["india_aqi", "india_aqi_pm"]
].corr().iloc[0, 1]

line(
    "Pearson correlation between targets",
    round(target_relationship, 4)
)

city_target_relationship = (
    df.groupby("city")
    .apply(
        lambda group: group[
            ["india_aqi", "india_aqi_pm"]
        ].corr().iloc[0, 1],
        include_groups=False
    )
    .reset_index(name="target_correlation")
)

city_target_relationship.to_csv(
    OUTPUT_DIR / "city_target_correlation.csv",
    index=False
)


# 9. SAVE FINAL REPORT


section("9. ANALYSIS SUMMARY")

line("Total records analysed", len(df))
line("Cities analysed", df["city"].nunique())
line("Analysis start date", df["date"].min().date())
line("Analysis end date", df["date"].max().date())

report_path = OUTPUT_DIR / "target_analysis_report.txt"

with open(report_path, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("\n" + "=" * 75)
print("TARGET ANALYSIS COMPLETED")
print("=" * 75)

print(f"\nReports saved in:\n{OUTPUT_DIR}")

print("\nGenerated files:")

for file in sorted(OUTPUT_DIR.iterdir()):
    print(f"- {file.name}")

print("\nPlease review the report before model development.")
