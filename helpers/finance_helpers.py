import os
import pandas as pd

from database.db_storage import get_model_results_from_postgres, get_predictions_from_postgres_by_asset



# Standardize asset symbols for consistent comparisons
def normalise_symbol(symbol):
    return str(symbol).strip().upper()


# Return core dissertation assets
def getAssets():

    return [
        {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Type": "Stock",
            "Description": "Apple Inc. is a primary dissertation stock asset used in the original model comparison."
        },
        {
            "Symbol": "AMZN",
            "Name": "Amazon.com Inc.",
            "Type": "Stock",
            "Description": "Amazon.com Inc. is a primary dissertation stock asset used in the original model comparison."
        },
        {
            "Symbol": "MSFT",
            "Name": "Microsoft Corporation",
            "Type": "Stock",
            "Description": "Microsoft Corporation is a primary dissertation stock asset used in the original model comparison."
        },
        {
            "Symbol": "SPY",
            "Name": "SPDR S&P 500 ETF",
            "Type": "ETF",
            "Description": "SPY is a primary dissertation ETF asset representing the S&P 500."
        },
        {
            "Symbol": "QQQ",
            "Name": "Invesco QQQ ETF",
            "Type": "ETF",
            "Description": "QQQ is a primary dissertation ETF asset with technology focused market exposure."
        }
    ]


# Retrieve saved model results
def getModelResults():

    # Try loading results from PostgreSQL first
    postgres_results = get_model_results_from_postgres()

    if postgres_results:
        return postgres_results

    generated_path = "data/generated_model_results.csv"
    default_path = "data/model_results.csv"

    # Prefer generated results if available
    if os.path.exists(generated_path) and os.path.getsize(generated_path) > 0:
        df = pd.read_csv(generated_path)

    else:
        df = pd.read_csv(default_path)

    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")


# Retrieve saved correlation data
def getCorrelations():

    df = pd.read_csv("data/correlations.csv")
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")


# Retrieve prediction results for a specific asset
def getPredictionsByAsset(asset):

    asset = normalise_symbol(asset)

    # Try loading predictions from PostgreSQL first
    postgres_predictions = get_predictions_from_postgres_by_asset(asset)

    if postgres_predictions:
        return postgres_predictions

    generated_path = "data/generated_predictions.csv"
    default_path = "data/predictions.csv"

    # Check generated predictions first
    if os.path.exists(generated_path) and os.path.getsize(generated_path) > 0:

        generated_df = pd.read_csv(generated_path)

        generated_df["Asset"] = (
            generated_df["Asset"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        filtered_generated_df = generated_df[generated_df["Asset"] == asset]

        if not filtered_generated_df.empty:

            filtered_generated_df = (
                filtered_generated_df
                .where(pd.notnull(filtered_generated_df), None)
            )

            return filtered_generated_df.to_dict(orient="records")

    # Fallback to default predictions file
    default_df = pd.read_csv(default_path)

    default_df["Asset"] = (
        default_df["Asset"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    filtered_default_df = default_df[default_df["Asset"] == asset]

    filtered_default_df = (
        filtered_default_df
        .where(pd.notnull(filtered_default_df), None)
    )

    return filtered_default_df.to_dict(orient="records")


# Retrieve asset information by symbol
def getAssetBySymbol(symbol):

    symbol = normalise_symbol(symbol)

    # Check dissertation asset list first
    for asset in getAssets():

        if normalise_symbol(asset["Symbol"]) == symbol:
            return asset

    # Check metadata dataset
    metadata_asset = getMetadataAssetBySymbol(symbol)

    if metadata_asset:
        return metadata_asset

    # Check historical dataset existence
    if checkHistoricalAssetExists(symbol):

        return {
            "Symbol": symbol,
            "Name": symbol,
            "Type": "Historical Asset",
            "Description": f"{symbol} exists in the historical dataset and can be tested using the Linear Regression and LSTM pipeline."
        }

    return None


# Retrieve metadata assets from CSV dataset
def getAvailableMetadataAssets(limit=None):

    metadata_path = "data/raw/symbols_valid_meta.csv"

    if not os.path.exists(metadata_path):
        return []

    df = pd.read_csv(metadata_path)

    df.columns = df.columns.str.strip()

    required_columns = ["Symbol", "Security Name", "ETF"]

    # Validate required columns
    if not set(required_columns).issubset(df.columns):
        return []

    # Keep only required columns
    df = df[required_columns].copy()

    df = df.dropna(subset=["Symbol", "Security Name"])

    # Clean values
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Security Name"] = df["Security Name"].astype(str).str.strip()
    df["ETF"] = df["ETF"].astype(str).str.strip().str.upper()

    # Optional asset limit
    if limit:
        df = df.head(limit)

    assets = []

    # Convert dataframe rows into asset dictionaries
    for _, row in df.iterrows():

        assets.append({
            "Symbol": row["Symbol"],
            "Name": row["Security Name"],
            "Type": "ETF" if row["ETF"] == "Y" else "Stock"
        })

    return assets


# Check whether an asset exists in historical datasets
def checkHistoricalAssetExists(symbol):

    symbol = normalise_symbol(symbol)

    stock_path = f"data/historical/stocks/{symbol}.csv"
    etf_path = f"data/historical/etfs/{symbol}.csv"

    return os.path.exists(stock_path) or os.path.exists(etf_path)


# Retrieve metadata asset information by symbol
def getMetadataAssetBySymbol(symbol):

    symbol = normalise_symbol(symbol)

    metadata_path = "data/raw/symbols_valid_meta.csv"

    if not os.path.exists(metadata_path):
        return None

    df = pd.read_csv(metadata_path)

    df.columns = df.columns.str.strip()

    required_columns = ["Symbol", "Security Name", "ETF"]

    # Validate required columns
    if not set(required_columns).issubset(df.columns):
        return None

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    # Find matching asset row
    row = df[df["Symbol"] == symbol]

    if row.empty:
        return None

    item = row.iloc[0]

    name = str(item["Security Name"]).strip()

    is_etf = str(item["ETF"]).strip().upper()

    asset_type = "ETF" if is_etf == "Y" else "Stock"

    # Return formatted metadata asset
    return {
        "Symbol": symbol,
        "Name": name,
        "Type": asset_type,
        "Description": f"{name} is a {asset_type.lower()} asset available in the historical market dataset."
    }


# Retrieve assets that already have saved model results
def getTestedAssets():

    model_results = getModelResults()

    tested_assets = []

    seen_symbols = set()

    for result in model_results:

        symbol = normalise_symbol(result.get("Asset", ""))

        # Skip invalid or duplicate assets
        if not symbol or symbol in seen_symbols:
            continue

        asset = getAssetBySymbol(symbol)

        if asset:

            asset["Recently_Tested"] = True

            tested_assets.append(asset)

        seen_symbols.add(symbol)

    return tested_assets