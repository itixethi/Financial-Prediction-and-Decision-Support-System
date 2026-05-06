import os
import pandas as pd

def getAssets():
    return [
        {"Symbol": "AAPL", "Name": "Apple Inc.", "Type": "Stock", "Description": "Apple Inc. is a selected stock asset used in the model comparison."},
        {"Symbol": "AMZN", "Name": "Amazon.com Inc.", "Type": "Stock", "Description": "Amazon showed the highest RMSE, suggesting greater volatility or noise."},
        {"Symbol": "MSFT", "Name": "Microsoft Corporation", "Type": "Stock", "Description": "Microsoft showed stable behaviour and was the only asset where Linear Regression slightly outperformed LSTM."},
        {"Symbol": "SPY", "Name": "SPDR S&P 500 ETF", "Type": "ETF", "Description": "SPY is an ETF representing the S&P 500 and produced low RMSE values."},
        {"Symbol": "QQQ", "Name": "Invesco QQQ ETF", "Type": "ETF", "Description": "QQQ is a technology-focused ETF and had strong correlation with SPY."}
    ]

def getModelResults():
    generated_path = "data/generated_model_results.csv"
    default_path = "data/model_results.csv"

    if os.path.exists(generated_path) and os.path.getsize(generated_path) > 0:
        df = pd.read_csv(generated_path)
    else:
        df = pd.read_csv(default_path)

    # Replace missing values/NaN with None so FastAPI can return valid JSON
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")

def getCorrelations():
    df = pd.read_csv("data/correlations.csv")
    return df.to_dict(orient="records")

def getPredictionsByAsset(asset):
    generated_path = "data/generated_predictions.csv"
    default_path = "data/predictions.csv"

    asset = asset.upper()

    # First try generated predictions
    if os.path.exists(generated_path) and os.path.getsize(generated_path) > 0:
        generated_df = pd.read_csv(generated_path)
        generated_df["Asset"] = generated_df["Asset"].astype(str)

        filtered_generated_df = generated_df[
            generated_df["Asset"].str.upper() == asset
        ]

        if not filtered_generated_df.empty:
            return filtered_generated_df.to_dict(orient="records")

    # If no generated rows exist for this asset, fall back to default predictions
    default_df = pd.read_csv(default_path)
    default_df["Asset"] = default_df["Asset"].astype(str)

    filtered_default_df = default_df[
        default_df["Asset"].str.upper() == asset
    ]

    return filtered_default_df.to_dict(orient="records")

def getAssetBySymbol(symbol):
    symbol = symbol.upper()

    # First check the original assets CSV/list
    assets = getAssets()

    for asset in assets:
        if str(asset["Symbol"]).upper() == symbol:
            return asset

    # Then check metadata CSV for wider historical assets
    metadata_asset = getMetadataAssetBySymbol(symbol)

    if metadata_asset:
        return metadata_asset

    # Then check if CSV exists in historical folder
    if checkHistoricalAssetExists(symbol):
        return {
            "Symbol": symbol,
            "Name": symbol,
            "Type": "Historical Asset",
            "Description": f"{symbol} exists in the historical dataset and can be tested using the Linear Regression and LSTM pipeline."
        }

    return None

def getAvailableMetadataAssets(limit=1000):
    metadata_path = "data/raw/symbols_valid_meta.csv"

    if not os.path.exists(metadata_path):
        return []

    df = pd.read_csv(metadata_path)

    df = df[["Symbol", "Security Name", "ETF"]].copy()
    df = df.dropna(subset=["Symbol", "Security Name"])

    assets = []

    for _, row in df.iterrows():
        symbol = str(row["Symbol"]).upper()
        is_etf = str(row["ETF"]).upper()

        assets.append({
            "Symbol": symbol,
            "Name": row["Security Name"],
            "Type": "ETF" if is_etf == "Y" else "Stock"
        })

    return assets


def checkHistoricalAssetExists(symbol):
    symbol = symbol.upper()

    stock_path = f"data/historical/stocks/{symbol}.csv"
    etf_path = f"data/historical/etfs/{symbol}.csv"

    return os.path.exists(stock_path) or os.path.exists(etf_path)

def getMetadataAssetBySymbol(symbol):
    metadata_path = "data/raw/symbols_valid_meta.csv"

    if not os.path.exists(metadata_path):
        return None

    df = pd.read_csv(metadata_path)
    df["Symbol"] = df["Symbol"].astype(str)

    row = df[df["Symbol"].str.upper() == symbol.upper()]

    if row.empty:
        return None

    item = row.iloc[0]

    return {
        "Symbol": str(item["Symbol"]).upper(),
        "Name": item["Security Name"],
        "Type": "ETF" if str(item["ETF"]).upper() == "Y" else "Stock",
        "Description": f"{item['Security Name']} is available in the historical metadata dataset."
    }

def getTestedAssets():
    model_results = getModelResults()
    tested_assets = []

    seen_symbols = set()

    for result in model_results:
        symbol = str(result.get("Asset", "")).upper()

        if not symbol or symbol in seen_symbols:
            continue

        asset = getAssetBySymbol(symbol)

        if asset:
            tested_assets.append(asset)

        seen_symbols.add(symbol)

    return tested_assets