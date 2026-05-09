import os
import shutil
import pandas as pd

SOURCE_BASE_PATH = "data/historical"

METADATA_PATH = "data/raw/symbols_valid_meta.csv"
PROJECT_STOCKS_PATH = "data/historical/stocks"
PROJECT_ETFS_PATH = "data/historical/etfs"

IMPORT_LIMIT = 1000
MIN_ROWS = 1000
REQUIRED_START_DATE = "2009-01-01"
REQUIRED_END_DATE = "2020-04-01"


# Create required project folders if they do not exist
def ensure_folders_exist():

    os.makedirs(PROJECT_STOCKS_PATH, exist_ok=True)
    os.makedirs(PROJECT_ETFS_PATH, exist_ok=True)


# Evaluate whether an asset meets import requirements
def evaluate_asset(symbol, is_etf):

    # Select correct source folder
    source_folder = "etfs" if is_etf else "stocks"

    source_file = os.path.join(
        SOURCE_BASE_PATH,
        source_folder,
        f"{symbol}.csv"
    )

    # Skip missing files
    if not os.path.exists(source_file):
        return None

    try:
        df = pd.read_csv(source_file)

    except Exception:
        return None

    required_columns = {"Date", "Close", "Adj Close", "Volume"}

    # Validate required dataset columns
    if not required_columns.issubset(set(df.columns)):
        return None

    # Clean date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.dropna(subset=["Date"])

    if df.empty:
        return None

    # Extract dataset range
    start_date = df["Date"].min()

    end_date = df["Date"].max()

    # Validate required historical coverage
    if start_date > pd.to_datetime(REQUIRED_START_DATE):
        return None

    if end_date < pd.to_datetime(REQUIRED_END_DATE):
        return None

    # Validate minimum dataset size
    if len(df) < MIN_ROWS:
        return None

    # Calculate average trading volume
    average_volume = (
        pd.to_numeric(df["Volume"], errors="coerce")
        .mean()
    )

    # Return evaluated asset details
    return {
        "Symbol": symbol,
        "Type": "ETF" if is_etf else "Stock",
        "Source_File": source_file,
        "Rows": len(df),
        "Start_Date": start_date,
        "End_Date": end_date,
        "Average_Volume": average_volume
    }


# Import strongest historical assets into project dataset
def import_best_historical_assets():

    ensure_folders_exist()

    metadata_df = pd.read_csv(METADATA_PATH)

    candidates = []

    # Evaluate all metadata assets
    for _, row in metadata_df.iterrows():

        symbol = str(row["Symbol"]).upper()

        is_etf = str(row["ETF"]).upper() == "Y"

        result = evaluate_asset(symbol, is_etf)

        if result:
            candidates.append(result)

    candidates_df = pd.DataFrame(candidates)

    # Handle empty candidate list
    if candidates_df.empty:
        print("No suitable assets found.")
        return

    # Rank assets by volume and dataset size
    candidates_df = candidates_df.sort_values(
        by=["Average_Volume", "Rows"],
        ascending=False
    )

    # Select top ranked assets
    selected_df = candidates_df.head(IMPORT_LIMIT)

    copied_count = 0

    # Copy selected asset files into project folders
    for _, row in selected_df.iterrows():

        symbol = row["Symbol"]

        asset_type = row["Type"]

        source_file = row["Source_File"]

        destination_folder = (
            PROJECT_ETFS_PATH
            if asset_type == "ETF"
            else PROJECT_STOCKS_PATH
        )

        destination_file = os.path.join(
            destination_folder,
            f"{symbol}.csv"
        )

        shutil.copy(source_file, destination_file)

        copied_count += 1

        print(f"Copied {symbol} ({asset_type})")

    # Save selection summary
    selected_df.to_csv(
        "data/historical_asset_selection.csv",
        index=False
    )

    print("\nImport complete.")
    print(f"Copied files: {copied_count}")
    print("Selection log saved to data/historical_asset_selection.csv")


# Run historical asset import directly from this file
if __name__ == "__main__":

    import_best_historical_assets()