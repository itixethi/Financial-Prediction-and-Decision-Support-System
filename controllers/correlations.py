from fastapi import Request
from fastapi.templating import Jinja2Templates

import pandas as pd

from model_pipeline.data_loader import load_asset_price_data
from database.db_storage import get_recent_model_results_for_correlation


# Generate correlation heatmap data using the latest shared analysis period
def calculate_latest_tested_asset_correlations(limit=5):

    # Load recent analysed model results
    model_results = get_recent_model_results_for_correlation(limit=200)

    # Handle empty results
    if not model_results:
        return {
            "labels": [],
            "matrix": [],
            "message": "No analysed model results are available for correlation analysis."
        }

    # Group results by shared analysis configuration
    grouped_results = {}

    for result in model_results:

        # Group using source, mode and evaluation range
        group_key = (
            str(result.get("Source", "kaggle")).strip(),
            str(result.get("Test_Mode", "original")).strip(),
            str(result.get("Evaluation_Start", "")).strip(),
            str(result.get("Evaluation_End", "")).strip()
        )

        grouped_results.setdefault(group_key, [])

        # Normalize asset symbol
        asset = str(result.get("Asset", "")).strip().upper()

        if not asset:
            continue

        # Avoid duplicate assets inside the same group
        existing_assets = {
            str(item.get("Asset", "")).strip().upper()
            for item in grouped_results[group_key]
        }

        if asset not in existing_assets:
            grouped_results[group_key].append(result)

    selected_group_key = None
    selected_results = []

    # Find first group containing at least 2 assets
    for group_key, group_items in grouped_results.items():

        if len(group_items) >= 2:
            selected_group_key = group_key
            selected_results = group_items[:limit]
            break

    # Handle no shared group
    if not selected_results:
        return {
            "labels": [],
            "matrix": [],
            "message": "No shared analysis period with at least two analysed assets was found."
        }

    # Extract shared configuration
    source, test_mode, evaluation_start, evaluation_end = selected_group_key

    price_frames = []

    # Load and prepare asset return series
    for item in selected_results:

        asset = str(item.get("Asset", "")).strip().upper()

        try:
            df = load_asset_price_data(asset, source=source)

            # Keep only required columns
            df = df[["Date", "Adj Close"]].copy()

            # Format and sort dates
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            # Filter to evaluation period
            df = df[
                (df["Date"] >= pd.to_datetime(evaluation_start)) &
                (df["Date"] <= pd.to_datetime(evaluation_end))
            ]

            # Calculate daily percentage returns
            df[asset] = df["Adj Close"].pct_change()

            # Store cleaned return series
            price_frames.append(df[["Date", asset]])

        # Skip assets with invalid/missing data
        except Exception:
            continue

    # Require at least 2 assets for correlation
    if len(price_frames) < 2:
        return {
            "labels": [],
            "matrix": [],
            "message": "Not enough price data was available for the selected shared analysis period."
        }

    # Merge all asset return series by date
    merged_df = price_frames[0]

    for frame in price_frames[1:]:
        merged_df = pd.merge(merged_df, frame, on="Date", how="inner")

    # Remove rows with missing values
    merged_df = merged_df.dropna()

    # Handle empty merged dataset
    if merged_df.empty:
        return {
            "labels": [],
            "matrix": [],
            "message": "No overlapping date range was found for the selected shared analysis period."
        }

    # Generate correlation matrix
    correlation_df = merged_df.drop(columns=["Date"]).corr()

    # Keep correlation values within valid heatmap range
    correlation_df = correlation_df.clip(-1, 1)

    # Return heatmap ready data
    return {
        "labels": correlation_df.columns.tolist(),
        "matrix": correlation_df.round(4).values.tolist(),
        "source": source,
        "test_mode": test_mode,
        "evaluation_start": evaluation_start,
        "evaluation_end": evaluation_end,
        "message": "Correlation heatmap generated from the most recent shared analysis period."
    }


async def correlationsView(request: Request, templates: Jinja2Templates):

    # Generate latest correlation data
    correlation_data = calculate_latest_tested_asset_correlations(limit=5)

    return templates.TemplateResponse(
        request=request,
        name="correlations.html",
        context={
            "correlation_data": correlation_data,
            "isAuthorized": False
        }
    )


# Helper function for reusable correlation access
def getLatestCorrelationData():

    return calculate_latest_tested_asset_correlations(limit=5)

