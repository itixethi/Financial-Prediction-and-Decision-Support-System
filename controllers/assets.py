from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.finance_helpers import getAssets, getAssetBySymbol, getModelResults, getPredictionsByAsset, getTestedAssets

async def assetsView(request: Request, templates: Jinja2Templates):
    query = request.query_params.get("query", "").strip().lower()

    original_assets = getAssets()
    tested_assets = getTestedAssets()

    combined_assets = []
    seen_symbols = set()

    for asset in original_assets + tested_assets:
        symbol = str(asset["Symbol"]).upper()

        if symbol not in seen_symbols:
            asset["Recently_Tested"] = any(
                str(tested["Symbol"]).upper() == symbol
                for tested in tested_assets
            )
            combined_assets.append(asset)
            seen_symbols.add(symbol)

    if query:
        combined_assets = [
            asset for asset in combined_assets
            if query in str(asset["Symbol"]).lower()
            or query in str(asset["Name"]).lower()
        ]

    return templates.TemplateResponse(
        request=request,
        name="assets.html",
        context={
            "assets": combined_assets,
            "query": query,
            "isAuthorized": False
        }
    )


async def assetDetailView(request: Request, templates: Jinja2Templates, symbol: str):
    symbol = symbol.upper()

    asset = getAssetBySymbol(symbol)
    model_results = getModelResults()
    predictions = getPredictionsByAsset(symbol)

    latest_model_result = None

    for result in model_results:
        if str(result.get("Asset", "")).upper() == symbol:
            latest_model_result = result
            break

    return templates.TemplateResponse(
        request=request,
        name="asset_detail.html",
        context={
            "asset": asset,
            "symbol": symbol,
            "model_result": latest_model_result,
            "prediction_count": len(predictions),
            "isAuthorized": False
        }
    )

