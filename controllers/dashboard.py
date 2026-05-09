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


# Display dashboard for a selected asset
async def dashboardView(request: Request, templates: Jinja2Templates):

    # Get selected filters from URL parameters
    selected_asset = request.query_params.get("asset", "AAPL").strip().upper()
    source = request.query_params.get("source", "kaggle").strip()
    test_mode = request.query_params.get("test_mode", "original").strip()
    evaluation_start = request.query_params.get("evaluation_start", "2010-02-02").strip()
    evaluation_end = request.query_params.get("evaluation_end", "2010-05-03").strip()

    # Load available assets
    assets = getAssets()
    metadata_assets = getAvailableMetadataAssets()

    # Try retrieving asset from main assets collection
    asset = getAssetBySymbol(selected_asset)

    # Fallback to metadata collection
    if asset is None:
        asset = getMetadataAssetBySymbol(selected_asset)

    # Handle assets existing only in historical datasets
    if asset is None and checkHistoricalAssetExists(selected_asset):
        asset = {
            "Symbol": selected_asset,
            "Name": "Additional historical asset",
            "Type": "Stock/ETF",
            "Description": "This asset exists in the historical dataset and can be tested using the model pipeline."
        }

    # Load saved model results and predictions
    model_results = getModelResults()
    predictions = getPredictionsByAsset(selected_asset)

    selected_model_result = None
    matching_results = []

    # Find matching model result using selected filters
    for result in model_results:

        result_asset = str(result.get("Asset", "")).strip().upper()
        result_test_mode = str(result.get("Test_Mode", "original")).strip()
        result_start = str(result.get("Evaluation_Start", "2010-02-02")).strip()
        result_end = str(result.get("Evaluation_End", "2010-05-03")).strip()

        if (
            result_asset == selected_asset.strip().upper()
            and result_test_mode == test_mode.strip()
            and result_start == evaluation_start.strip()
            and result_end == evaluation_end.strip()
        ):
            matching_results.append(result)

        # Use first exact matching result
        if matching_results:
            selected_model_result = matching_results[0]

        # Fallback to any available result for the asset
        else:
            for result in model_results:
                if str(result.get("Asset", "")).strip().upper() == selected_asset.strip().upper():
                    selected_model_result = result
                    break

    # Render dashboard page
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
            "source": source,
            "isAuthorized": False
        }
    )