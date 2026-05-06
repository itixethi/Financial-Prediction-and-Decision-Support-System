from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.live_data_helpers import getLiveMarketData

async def liveMarketView(request: Request, templates: Jinja2Templates, symbol: str):
    market_data = getLiveMarketData(symbol)

    return templates.TemplateResponse(
        request=request,
        name="live_market.html",
        context={
            "symbol": symbol.upper(),
            "market_data": market_data,
            "isAuthorized": False
        }
    )