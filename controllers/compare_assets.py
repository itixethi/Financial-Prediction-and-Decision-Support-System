from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.finance_helpers import getModelResults, getMetadataAssetBySymbol


# Find the latest saved model result matching the selected filters
def find_latest_matching_result(model_results, asset, source, test_mode, evaluation_start, evaluation_end):

    # Normalize incoming values
    asset = asset.strip().upper()
    source = source.strip()
    test_mode = test_mode.strip()
    evaluation_start = evaluation_start.strip()
    evaluation_end = evaluation_end.strip()

    # Store matching records
    matching_results = []

    # Loop through all saved model results
    for result in model_results:

        # Normalize stored values for comparison
        result_asset = str(result.get("Asset", "")).strip().upper()
        result_source = str(result.get("Source", "kaggle")).strip()
        result_test_mode = str(result.get("Test_Mode", "original")).strip()
        result_start = str(result.get("Evaluation_Start", "2010-02-02")).strip()
        result_end = str(result.get("Evaluation_End", "2010-05-03")).strip()

        # Check if all filters match
        if (
            result_asset == asset and
            result_source == source and
            result_test_mode == test_mode and
            result_start == evaluation_start and
            result_end == evaluation_end
        ):
            matching_results.append(result)

    # Return None if no matching result exists
    if not matching_results:
        return None

    # Return latest matching result
    return matching_results[-1]


# Generate comparison interpretation using LSTM RMSE
def build_comparison_interpretation(asset1_symbol, asset2_symbol, asset1_result, asset2_result):

    # Extract RMSE values
    asset1_lstm = float(asset1_result["LSTM_RMSE"])
    asset2_lstm = float(asset2_result["LSTM_RMSE"])

    # Lower RMSE indicates stronger prediction accuracy
    if asset1_lstm < asset2_lstm:
        return f"{asset1_symbol} produced the lower LSTM RMSE, suggesting stronger predictive performance for the selected test period."

    elif asset2_lstm < asset1_lstm:
        return f"{asset2_symbol} produced the lower LSTM RMSE, suggesting stronger predictive performance for the selected test period."

    # Handle equal RMSE values
    else:
        return f"{asset1_symbol} and {asset2_symbol} produced the same LSTM RMSE for the selected test period."


# Compare two selected assets
async def compareAssetsView(request: Request, templates: Jinja2Templates):

    # Get selected asset symbols
    asset1_symbol = request.query_params.get("asset1", "AAPL").upper().strip().upper()
    asset2_symbol = request.query_params.get("asset2", "GOOGL").upper().strip().upper()

    # Get comparison filters
    source = request.query_params.get("source", "kaggle").strip()
    test_mode = request.query_params.get("test_mode", "original").strip()
    evaluation_start = request.query_params.get("evaluation_start", "2010-02-02").strip()
    evaluation_end = request.query_params.get("evaluation_end", "2010-05-03").strip()

    # Load all saved model results
    model_results = getModelResults()

    # Find matching result for asset 1
    asset1_result = find_latest_matching_result(
        model_results,
        asset1_symbol,
        source,
        test_mode,
        evaluation_start,
        evaluation_end
    )

    # Find matching result for asset 2
    asset2_result = find_latest_matching_result(
        model_results,
        asset2_symbol,
        source,
        test_mode,
        evaluation_start,
        evaluation_end
    )

    # Load metadata for both assets
    asset1 = getMetadataAssetBySymbol(asset1_symbol)
    asset2 = getMetadataAssetBySymbol(asset2_symbol)

    # Store missing analysis messages
    missing_messages = []

    # Check if asset 1 result exists
    if asset1_result is None:
        missing_messages.append(
            f"{asset1_symbol} has no saved analysis for {test_mode}, {evaluation_start} to {evaluation_end}."
        )

    # Check if asset 2 result exists
    if asset2_result is None:
        missing_messages.append(
            f"{asset2_symbol} has no saved analysis for {test_mode}, {evaluation_start} to {evaluation_end}."
        )

    # Comparison only works if both results exist
    comparison_ready = asset1_result is not None and asset2_result is not None

    interpretation = None

    # Build comparison summary
    if comparison_ready:
        interpretation = build_comparison_interpretation(
            asset1_symbol,
            asset2_symbol,
            asset1_result,
            asset2_result
        )

    # Render comparison page
    return templates.TemplateResponse(
        request=request,
        name="compare_assets.html",
        context={
            "asset1_symbol": asset1_symbol,
            "asset2_symbol": asset2_symbol,
            "asset1": asset1,
            "asset2": asset2,
            "asset1_model": asset1_result,
            "asset2_model": asset2_result,
            "comparison_ready": comparison_ready,
            "missing_messages": missing_messages,
            "interpretation": interpretation,
            "source": source,
            "test_mode": test_mode,
            "evaluation_start": evaluation_start,
            "evaluation_end": evaluation_end,
            "isAuthorized": False
        }
    )