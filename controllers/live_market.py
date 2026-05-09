from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from helpers.live_data_helpers import getLiveMarketData

from model_pipeline.data_loader import load_asset_price_data
from database.db_storage import get_live_market_data_from_postgres, save_live_market_data_to_postgres

# Display live market page for a selected asset
async def liveMarketView(request: Request, templates: Jinja2Templates, symbol: str):

    # Load stored live market data
    market_data = getLiveMarketData(symbol)

    # Render live market page
    return templates.TemplateResponse(
        request=request,
        name="live_market.html",
        context={
            "symbol": symbol.upper(),
            "market_data": market_data,
            "isAuthorized": False
        }
    )


# API endpoint for retrieving live market data
async def apiLiveMarket(symbol: str):

    # Normalize asset symbol
    symbol = symbol.upper()

    # Check if data already exists in PostgreSQL
    stored_data = getLiveMarketData(symbol)

    # Return stored data if available
    if stored_data:
        return JSONResponse(
            content={
                "symbol": symbol,
                "source": "postgres",
                "price_data": stored_data
            }
        )

    # Fetch live market data using yfinance
    live_df = load_asset_price_data(symbol, source="live")

    # Save fetched data into PostgreSQL
    save_live_market_data_to_postgres(symbol, live_df)

    # Reload saved data from PostgreSQL
    stored_data = get_live_market_data_from_postgres(symbol)

    # Return saved live data response
    return JSONResponse(
        content={
            "symbol": symbol,
            "source": "yfinance_postgres_saved",
            "price_data": stored_data
        }
    )