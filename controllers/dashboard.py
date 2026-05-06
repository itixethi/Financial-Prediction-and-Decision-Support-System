from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.finance_helpers import (
    getAssets,
    getModelResults,
    getPredictionsByAsset,
    getAssetBySymbol,
    getAvailableMetadataAssets,
    checkHistoricalAssetExists,
    getMetadataAssetBySymbol
)


async def dashboardView(request: Request, templates: Jinja2Templates):
    selected_asset = request.query_params.get("asset", "AAPL").upper()
    test_mode = request.query_params.get("test_mode", "original")
    evaluation_start = request.query_params.get("evaluation_start", "2010-02-02")
    evaluation_end = request.query_params.get("evaluation_end", "2010-05-03")

    assets = getAssets()
    metadata_assets = getAvailableMetadataAssets()

    asset = getAssetBySymbol(selected_asset)

    if asset is None:
        asset = getMetadataAssetBySymbol(selected_asset)

    if asset is None and checkHistoricalAssetExists(selected_asset):
        asset = {
            "Symbol": selected_asset,
            "Name": "Additional historical asset",
            "Type": "Stock/ETF",
            "Description": "This asset exists in the historical dataset and can be tested using the model pipeline."
        }

    model_results = getModelResults()
    predictions = getPredictionsByAsset(selected_asset)

    selected_model_result = None

    for result in model_results:
        if str(result["Asset"]).upper() == selected_asset:
            selected_model_result = result
            break

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "assets": assets,
            "metadata_assets": metadata_assets,
            "selected_asset": selected_asset,
            "asset": asset,
            "model_result": selected_model_result,
            "predictions": predictions,
            "test_mode": test_mode,
            "evaluation_start": evaluation_start,
            "evaluation_end": evaluation_end,
            "isAuthorized": False
        }
    )