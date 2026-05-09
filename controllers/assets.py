from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.finance_helpers import getAssets, getAssetBySymbol, getModelResults, getPredictionsByAsset, getTestedAssets

# Display all assets and support search filtering
async def assetsView(request: Request, templates: Jinja2Templates):

    # Get search query from URL
    query = request.query_params.get("query", "").strip().lower()

    # Load assets collections
    original_assets = getAssets()
    tested_assets = getTestedAssets()

    # Store merged unique assets
    combined_assets = []
    seen_symbols = set()

    # Merge original and analysed assets without duplicates
    for asset in original_assets + tested_assets:

        # Normalize symbol format
        symbol = str(asset["Symbol"]).upper()

        if symbol not in seen_symbols:

            # Flag assets that exist in tested collection
            asset["Recently_Tested"] = any(
                str(tested["Symbol"]).upper() == symbol
                for tested in tested_assets
            )

            combined_assets.append(asset)
            seen_symbols.add(symbol)

    # Apply search filter if query exists
    if query:
        combined_assets = [
            asset for asset in combined_assets
            if query in str(asset["Symbol"]).lower()
            or query in str(asset["Name"]).lower()
        ]

    # Render assets page
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

    # Load asset data and related predictions
    asset = getAssetBySymbol(symbol)
    model_results = getModelResults()
    predictions = getPredictionsByAsset(symbol)

    # Store matching model result
    latest_model_result = None

    # Find latest model result for the asset
    for result in model_results:
        if str(result.get("Asset", "")).upper() == symbol:
            latest_model_result = result
            break

    # Render asset detail page
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

