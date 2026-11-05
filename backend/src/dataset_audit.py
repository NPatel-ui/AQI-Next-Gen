from pathlib import Path
import pandas as pd
import numpy as np



ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT_DIR / "data" / "raw" / "air_quality_daily.csv"
CITIES_PATH = ROOT_DIR / "data" / "raw" / "cities.csv"
REPORT_DIR = ROOT_DIR / "data" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)



print("\n" + "=" * 65)
print("             AQI FORECASTER - DATASET AUDIT")
print("=" * 65)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

if not CITIES_PATH.exists():
    raise FileNotFoundError(f"Cities file not found: {CITIES_PATH}")

df = pd.read_csv(DATA_PATH)
cities_df = pd.read_csv(CITIES_PATH)

# Standardize date column
if "date" not in df.columns or "city" not in df.columns:
    raise ValueError("Expected 'date' and 'city' columns were not found.")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["city"] = df["city"].astype("string").str.strip()


report = []

def add_section(title):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)

def add_line(label, value):
    report.append(f"{label:<35}: {value}")

add_section("1. DATASET OVERVIEW")

add_line("Total records", f"{len(df):,}")
add_line("Total columns", len(df.columns))
add_line("Unique cities", df["city"].nunique())
add_line("Start date", df["date"].min())
add_line("End date", df["date"].max())
add_line("Cities reference records", len(cities_df))

report.append("\nColumns:")
report.extend([f"- {column}" for column in df.columns])


add_section("2. DATA QUALITY")

add_line("Duplicate rows", df.duplicated().sum())
add_line(
    "Duplicate city-date records",
    df.duplicated(subset=["city", "date"]).sum()
)
add_line("Missing dates", df["date"].isna().sum())
add_line("Missing city names", df["city"].isna().sum())

missing = df.isna().sum()
report.append("\nMissing values by column:")

for column, count in missing.items():
    percentage = (count / len(df)) * 100
    report.append(
        f"{column:<30} {count:>8} ({percentage:.2f}%)"
    )


add_section("3. CITY COVERAGE")

city_counts = (
    df.groupby("city")
    .agg(
        records=("date", "count"),
        first_date=("date", "min"),
        last_date=("date", "max")
    )
    .reset_index()
    .sort_values("city")
)

city_counts.to_csv(
    REPORT_DIR / "city_coverage.csv",
    index=False
)

report.append("\nCity record counts:")

for _, row in city_counts.iterrows():
    report.append(
        f"{row['city']:<25} "
        f"Records: {row['records']:>5} | "
        f"{row['first_date'].date()} to {row['last_date'].date()}"
    )



add_section("4. REQUIRED CITY AVAILABILITY")

required_cities = [
    "Delhi",
    "Gurugram",
    "Mumbai",
    "Nagpur"
]

available_cities = set(df["city"].dropna().str.lower())

for city in required_cities:
    status = (
        "AVAILABLE"
        if city.lower() in available_cities
        else "NOT AVAILABLE"
    )
    add_line(city, status)


add_section("5. AQI TARGET ANALYSIS")

targets = [
    "india_aqi",
    "india_aqi_pm"
]

for target in targets:
    if target not in df.columns:
        add_line(target, "COLUMN NOT FOUND")
        continue

    values = pd.to_numeric(df[target], errors="coerce")

    report.append(f"\nTarget: {target}")
    add_line("Valid records", values.notna().sum())
    add_line("Missing records", values.isna().sum())

    if values.notna().any():
        add_line("Minimum", round(values.min(), 2))
        add_line("Maximum", round(values.max(), 2))
        add_line("Mean", round(values.mean(), 2))
        add_line("Median", round(values.median(), 2))
        add_line("Standard deviation", round(values.std(), 2))

        report.append("\nPercentiles:")

        for percentile in [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]:
            value = values.quantile(percentile)
            report.append(
                f"{percentile * 100:>5.0f}% : {value:.2f}"
            )



add_section("6. AQI CATEGORY DISTRIBUTION")

category_columns = [
    "india_aqi_category",
    "india_aqi_pm_category"
]

for column in category_columns:
    if column not in df.columns:
        continue

    report.append(f"\n{column}:")

    counts = df[column].value_counts(dropna=False)

    for category, count in counts.items():
        percentage = count / len(df) * 100
        report.append(
            f"{str(category):<25} {count:>8} ({percentage:.2f}%)"
        )

# --------------------
# POLLUTANT ANALYSIS
# --------------------

add_section("7. POLLUTANT ANALYSIS")

pollutant_columns = [
    "pm2_5_mean",
    "pm2_5_max",
    "pm10_mean",
    "pm10_max",
    "no2_mean",
    "so2_mean",
    "o3_8h_max",
    "co_8h_max",
    "dust_mean",
    "aod_mean"
]

pollutant_stats = []

for column in pollutant_columns:
    if column not in df.columns:
        continue

    values = pd.to_numeric(df[column], errors="coerce")

    pollutant_stats.append({
        "pollutant": column,
        "valid_records": values.notna().sum(),
        "missing_records": values.isna().sum(),
        "minimum": values.min(),
        "maximum": values.max(),
        "mean": values.mean(),
        "median": values.median()
    })

    report.append(
        f"{column:<20} "
        f"Min: {values.min():.3f} | "
        f"Max: {values.max():.3f} | "
        f"Mean: {values.mean():.3f}"
    )

pd.DataFrame(pollutant_stats).to_csv(
    REPORT_DIR / "pollutant_statistics.csv",
    index=False
)

# --------------------
# DOMINANT POLLUTANT
# --------------------

add_section("8. DOMINANT POLLUTANT DISTRIBUTION")

if "dominant_pollutant" in df.columns:
    dominant_counts = df["dominant_pollutant"].value_counts(
        dropna=False
    )

    for pollutant, count in dominant_counts.items():
        percentage = count / len(df) * 100
        report.append(
            f"{str(pollutant):<20} "
            f"{count:>8} ({percentage:.2f}%)"
        )

# --------------------
# DAILY DATA CONTINUITY
# --------------------

add_section("9. DAILY DATA CONTINUITY")

df_sorted = df.sort_values(["city", "date"]).copy()

df_sorted["date_gap"] = (
    df_sorted.groupby("city")["date"].diff().dt.days
)

gap_counts = df_sorted["date_gap"].value_counts().sort_index()

report.append("\nDate gap distribution:")

for gap, count in gap_counts.items():
    report.append(f"{gap} day(s): {count:,} records")



report_text = "\n".join(report)

report_path = REPORT_DIR / "dataset_audit_report.txt"

with open(report_path, "w", encoding="utf-8") as file:
    file.write(report_text)

print(report_text)

print("\n" + "=" * 65)
print("AUDIT COMPLETED")
print("=" * 65)
print(f"Report saved: {report_path}")
print(f"City coverage saved: {REPORT_DIR / 'city_coverage.csv'}")
print(f"Pollutant statistics saved: {REPORT_DIR / 'pollutant_statistics.csv'}")