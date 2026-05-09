import os
import pandas as pd
import yfinance as yf

# Project based paths
# These point to files inside my Finance Prediction.
HISTORICAL_BASE_PATH = "data/historical"
RAW_METADATA_PATH = "data/raw/symbols_valid_meta.csv"


def load_kaggle_asset_data(symbol: str) -> pd.DataFrame:
    """
    Loads historical dissertation price data from the project data folder.

    Expected structure:
    data/historical/stocks/AAPL.csv
    data/historical/etfs/SPY.csv
    """

    symbol = symbol.upper().strip()

    stock_path = os.path.join(HISTORICAL_BASE_PATH, "stocks", f"{symbol}.csv")
    etf_path = os.path.join(HISTORICAL_BASE_PATH, "etfs", f"{symbol}.csv")

    if os.path.exists(stock_path):
        file_path = stock_path
    elif os.path.exists(etf_path):
        file_path = etf_path
    else:
        raise ValueError(
            f"{symbol} was not found in data/historical/stocks or data/historical/etfs."
        )

    df = pd.read_csv(file_path)

    # Keep the same modelling fields used in my EDA dissertation.
    # Open, High, and Low are deliberately ignored to reduce noise.
    df = df[["Date", "Close", "Adj Close", "Volume"]]

    df["Date"] = pd.to_datetime(df["Date"])

    # Dissertation historical window
    df = df[df["Date"] >= "2009-01-01"]
    df = df[df["Date"] <= "2020-04-01"]

    df = df.sort_values("Date").reset_index(drop=True)

    return df


def load_live_asset_data(symbol: str, period: str = "5y") -> pd.DataFrame:
    """
    Loads newer market data using yfinance for live/prototype mode.
    This does not replace the historical dissertation dataset.
    """

    symbol = symbol.upper().strip()

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval="1d")

    if df.empty:
        raise ValueError(f"No live market data found for {symbol}.")

    df = df.reset_index()
    # yfinance can return timezone aware dates, remove timezone for consistency
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

    df = df[["Date", "Close", "Volume"]]
    df["Adj Close"] = df["Close"]

    df = df.sort_values("Date").reset_index(drop=True)

    return df


def load_asset_price_data(symbol: str, source: str = "kaggle") -> pd.DataFrame:
    """
    Main loader used by the model pipeline.

    source="kaggle" loads the self contained historical dissertation files.
    source="live" loads newer external data for future live testing.
    """

    source = source.lower().strip()

    if source == "kaggle":
        return load_kaggle_asset_data(symbol)

    if source == "live":
        return load_live_asset_data(symbol)

    raise ValueError("Invalid source. Use 'kaggle' or 'live'.")