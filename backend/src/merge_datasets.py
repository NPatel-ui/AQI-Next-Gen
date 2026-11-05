
from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

AQ_FILE = RAW_DIR / "air_quality_daily.csv"
WEATHER_FILE = RAW_DIR / "weather_daily.csv"
CITIES_FILE = RAW_DIR / "cities.csv"

OUTPUT_FILE = PROCESSED_DIR / "merged_daily.csv"


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading datasets...")

    aq = pd.read_csv(AQ_FILE, parse_dates=["date"])
    weather = pd.read_csv(WEATHER_FILE, parse_dates=["date"])
    cities = pd.read_csv(CITIES_FILE)

    # Validate required columns
    for name, df in [
        ("Air quality", aq),
        ("Weather", weather),
    ]:
        required = {"date", "city"}
        if not required.issubset(df.columns):
            raise ValueError(f"{name} dataset is missing required columns.")

        if df[["date", "city"]].isna().any().any():
            raise ValueError(f"{name} contains missing city/date keys.")

        if df.duplicated(["city", "date"]).any():
            raise ValueError(f"{name} contains duplicate city-date records.")

    if cities["city"].isna().any() or cities["city"].duplicated().any():
        raise ValueError("City metadata has missing or duplicate city names.")

    # Validate city coverage
    aq_cities = set(aq["city"])
    weather_cities = set(weather["city"])
    metadata_cities = set(cities["city"])

    if aq_cities != weather_cities:
        raise ValueError("Air-quality and weather city coverage differs.")

    if not aq_cities.issubset(metadata_cities):
        raise ValueError("Some cities are missing from cities.csv.")

    print("Merging air quality and weather...")

    merged = aq.merge(
        weather,
        on=["city", "date"],
        how="left",
        validate="one_to_one",
        indicator=True
    )

    unmatched = merged["_merge"] != "both"

    if unmatched.any():
        raise ValueError(
            f"{unmatched.sum()} air-quality records have no weather match."
        )

    merged.drop(columns="_merge", inplace=True)

    print("Adding city metadata...")

    merged = merged.merge(
        cities,
        on="city",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    unmatched_metadata = merged["_merge"] != "both"

    if unmatched_metadata.any():
        raise ValueError("Some records have no matching city metadata.")

    merged.drop(columns="_merge", inplace=True)

    # Sort records consistently
    merged.sort_values(
        by=["city", "date"],
        inplace=True
    )

    merged.reset_index(drop=True, inplace=True)

    # Final validation
    if merged.isna().any().any():
        missing = merged.isna().sum()
        raise ValueError(
            f"Missing values detected:\n{missing[missing > 0]}"
        )

    if merged.duplicated(["city", "date"]).any():
        raise ValueError("Duplicate records found after merging.")

    # Save processed dataset
    merged.to_csv(OUTPUT_FILE, index=False)

    print("\nMERGE COMPLETED SUCCESSFULLY")
    print(f"Total records: {len(merged):,}")
    print(f"Total columns: {len(merged.columns)}")
    print(f"Unique cities: {merged['city'].nunique()}")
    print(f"Date range: {merged['date'].min().date()} to "
          f"{merged['date'].max().date()}")
    print(f"Missing values: {merged.isna().sum().sum()}")
    print(f"Duplicate city-date records: "
          f"{merged.duplicated(['city', 'date']).sum()}")
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
