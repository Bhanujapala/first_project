import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "raw_books.csv"
OUTPUT_FILE = DATA_DIR / "cleaned_books.csv"


# ---------------------------------------------------------
# FIXED GBP TO INR CONVERSION RATE
# ---------------------------------------------------------

GBP_TO_INR = 105.50


# ---------------------------------------------------------
# STAR RATING MAPPING
# ---------------------------------------------------------

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


# ---------------------------------------------------------
# AVAILABILITY PARSER
# ---------------------------------------------------------

def parse_availability(value):

    if pd.isna(value):
        return None

    text = str(value).strip().lower()

    if "in stock" in text:
        return True

    if "out of stock" in text:
        return False

    return None


# ---------------------------------------------------------
# CLEAN BOOK DATA
# ---------------------------------------------------------

def clean_books(df):

    clean = df.copy()

    # -----------------------------------------------------
    # PRICE
    # Remove £ symbol and convert to float
    # -----------------------------------------------------

    clean["price_gbp"] = (
        clean["price"]
        .astype(str)
        .str.replace("£", "", regex=False)
        .str.replace("Â", "", regex=False)
        .str.strip()
    )

    clean["price_gbp"] = pd.to_numeric(
        clean["price_gbp"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # STAR RATING
    # Convert One/Five -> 1/5
    # -----------------------------------------------------

    clean["rating"] = clean["star_rating"].map(RATING_MAP)

    # -----------------------------------------------------
    # AVAILABILITY
    # Convert text -> Boolean
    # -----------------------------------------------------

    clean["in_stock"] = clean["availability"].apply(
        parse_availability
    )

    # -----------------------------------------------------
    # HANDLE MISSING NUMERIC VALUES
    # -----------------------------------------------------

    if clean["price_gbp"].isna().any():

        median_price = clean["price_gbp"].median()

        clean["price_gbp"] = clean["price_gbp"].fillna(
            median_price
        )

    if clean["rating"].isna().any():

        median_rating = clean["rating"].median()

        clean["rating"] = clean["rating"].fillna(
            median_rating
        )

    # Rating must be integer
    clean["rating"] = (
        clean["rating"]
        .round()
        .astype(int)
    )

    # -----------------------------------------------------
    # REMOVE ROWS WHERE AVAILABILITY COULD NOT BE PARSED
    # -----------------------------------------------------

    clean = clean.dropna(
        subset=["title", "category", "in_stock"]
    ).copy()

    # Convert to Boolean
    clean["in_stock"] = clean["in_stock"].astype(bool)

    # -----------------------------------------------------
    # GBP -> INR
    # -----------------------------------------------------

    clean["price_inr"] = (
        clean["price_gbp"] * GBP_TO_INR
    ).round(2)

    # -----------------------------------------------------
    # FINAL COLUMNS
    # -----------------------------------------------------

    clean = clean[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ]

    return clean


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("STARTING DATA CLEANING")
    print("=" * 60)

    # Read raw data
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print(f"\nRaw rows: {len(df)}")

    # Clean data
    clean_df = clean_books(df)

    print(f"Clean rows: {len(clean_df)}")

    # -----------------------------------------------------
    # DISPLAY DATA TYPES
    # -----------------------------------------------------

    print("\nData types:")
    print(clean_df.dtypes)

    # -----------------------------------------------------
    # DISPLAY FIRST 5 ROWS
    # -----------------------------------------------------

    print("\nFirst 5 cleaned records:")
    print(clean_df.head())

    # -----------------------------------------------------
    # DISPLAY MISSING VALUES
    # -----------------------------------------------------

    print("\nMissing values:")
    print(clean_df.isnull().sum())

    # -----------------------------------------------------
    # SAVE CLEANED DATA
    # -----------------------------------------------------

    clean_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCleaned data saved to:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("CLEANING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()