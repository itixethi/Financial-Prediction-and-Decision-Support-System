import yfinance as yf

# Retrieve recent live market data using yfinance
def getLiveMarketData(symbol):

    # Create yfinance ticker object
    ticker = yf.Ticker(symbol)

    # Load last 5 days of daily market data
    history = ticker.history(period="5d", interval="1d")

    # Handle missing market data
    if history.empty:
        return {
            "symbol": symbol.upper(),
            "error": "No market data found."
        }

    # Convert index into dataframe column
    history = history.reset_index()

    # Get latest trading row
    latest_row = history.iloc[-1]

    price_data = []

    # Format historical price data
    for _, row in history.iterrows():

        price_data.append({
            "date": str(row["Date"].date()),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        })

    # Return structured market response
    return {
        "symbol": symbol.upper(),
        "latest_close": round(float(latest_row["Close"]), 2),
        "latest_volume": int(latest_row["Volume"]),
        "price_data": price_data
    }