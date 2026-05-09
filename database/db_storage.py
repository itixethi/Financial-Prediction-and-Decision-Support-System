import os
import pandas as pd
from datetime import datetime

from database.database import SessionLocal
from database.models import Asset, HistoricalPrice, ExperimentRun, ModelResult, Prediction, LiveMarketPrice


PRIMARY_RESEARCH_ASSETS = {"AAPL", "AMZN", "MSFT", "SPY", "QQQ"}


# Determine whether an asset is a stock or ETF
def get_asset_type(symbol: str) -> str:

    stock_path = f"data/historical/stocks/{symbol}.csv"
    etf_path = f"data/historical/etfs/{symbol}.csv"

    # ETF file exists
    if os.path.exists(etf_path):
        return "ETF"

    # Stock file exists
    if os.path.exists(stock_path):
        return "Stock"

    # Asset not found
    return "Unknown"


# Retrieve metadata for an asset
def get_asset_metadata(symbol: str):

    metadata_path = "data/raw/symbols_valid_meta.csv"

    # Fallback metadata if CSV does not exist
    if not os.path.exists(metadata_path):
        return {
            "name": symbol,
            "asset_type": get_asset_type(symbol),
            "description": "Historical asset imported into the project."
        }

    metadata_df = pd.read_csv(metadata_path)
    metadata_df["Symbol"] = metadata_df["Symbol"].astype(str)

    # Find matching symbol
    row = metadata_df[metadata_df["Symbol"].str.upper() == symbol.upper()]

    # Fallback metadata if symbol not found
    if row.empty:
        return {
            "name": symbol,
            "asset_type": get_asset_type(symbol),
            "description": "Historical asset imported into the project."
        }

    item = row.iloc[0]

    # Return cleaned metadata
    return {
        "name": item["Security Name"],
        "asset_type": "ETF" if str(item["ETF"]).upper() == "Y" else "Stock",
        "description": f"{item['Security Name']} is part of the historical market dataset."
    }


# Insert or update asset information in PostgreSQL
def upsert_asset(db, symbol: str):

    symbol = symbol.upper()
    metadata = get_asset_metadata(symbol)

    # Check if asset already exists
    asset = db.query(Asset).filter(Asset.symbol == symbol).first()

    # Assign research grouping
    research_group = (
        "primary_dissertation_asset"
        if symbol in PRIMARY_RESEARCH_ASSETS
        else "extended_historical"
    )

    # Update existing asset
    if asset:
        asset.name = metadata["name"]
        asset.asset_type = metadata["asset_type"]
        asset.description = metadata["description"]
        asset.research_group = research_group
        return asset

    # Create new asset record
    asset = Asset(
        symbol=symbol,
        name=metadata["name"],
        asset_type=metadata["asset_type"],
        source="kaggle",
        description=metadata["description"],
        research_group=research_group
    )

    db.add(asset)
    db.flush()

    return asset


# Import historical CSV price data into PostgreSQL
def import_historical_prices_to_postgres(limit_assets=None):

    db = SessionLocal()

    try:
        asset_files = []

        # Scan stock and ETF folders
        for folder, asset_type in [
            ("data/historical/stocks", "Stock"),
            ("data/historical/etfs", "ETF")
        ]:

            if not os.path.exists(folder):
                continue

            for filename in os.listdir(folder):

                if filename.endswith(".csv"):
                    symbol = filename.replace(".csv", "").upper()

                    asset_files.append(
                        (symbol, os.path.join(folder, filename), asset_type)
                    )

        # Optional import limit
        if limit_assets:
            asset_files = asset_files[:limit_assets]

        imported_assets = 0
        imported_prices = 0

        # Import each asset file
        for symbol, file_path, asset_type in asset_files:

            print(f"Importing {symbol}...")

            upsert_asset(db, symbol)

            # Skip already imported assets
            existing_count = (
                db.query(HistoricalPrice)
                .filter(HistoricalPrice.asset_symbol == symbol)
                .count()
            )

            if existing_count > 0:
                print(f"Skipping {symbol}, prices already imported.")
                continue

            df = pd.read_csv(file_path)

            required_columns = ["Date", "Close", "Adj Close", "Volume"]

            # Validate required columns
            if not set(required_columns).issubset(df.columns):
                print(f"Skipping {symbol}, missing required columns.")
                continue

            # Clean dataset
            df = df[required_columns].copy()
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date", "Close"])

            price_objects = []

            # Convert rows into SQLAlchemy objects
            for _, row in df.iterrows():

                price_objects.append(
                    HistoricalPrice(
                        asset_symbol=symbol,
                        date=row["Date"].date(),
                        close=float(row["Close"]),
                        adj_close=float(row["Adj Close"]) if pd.notnull(row["Adj Close"]) else None,
                        volume=float(row["Volume"]) if pd.notnull(row["Volume"]) else None
                    )
                )

            # Bulk insert price data
            db.bulk_save_objects(price_objects)
            db.commit()

            imported_assets += 1
            imported_prices += len(price_objects)

        print("Historical import complete.")
        print(f"Assets processed: {imported_assets}")
        print(f"Price rows imported: {imported_prices}")

    finally:
        db.close()


# Save completed analysis results into PostgreSQL
def save_analysis_result_to_postgres(result: dict):

    db = SessionLocal()

    try:
        symbol = result["asset"].upper()

        upsert_asset(db, symbol)

        # Create experiment run record
        experiment_run = ExperimentRun(
            asset_symbol=symbol,
            source=result["source"],
            test_mode=result["test_mode"],
            evaluation_start=pd.to_datetime(result["evaluation_start"]).date(),
            evaluation_end=pd.to_datetime(result["evaluation_end"]).date(),
            lookback_days=result["lookback_days"],
            created_at=datetime.utcnow()
        )

        db.add(experiment_run)
        db.flush()

        # Save model evaluation metrics
        model_result = ModelResult(
            experiment_run_id=experiment_run.id,
            asset_symbol=symbol,
            linear_regression_rmse=float(result["linear_regression"]["rmse"]),
            lstm_rmse=float(result["lstm"]["rmse"]),
            best_model=result["best_model"],
            lstm_improvement_percent=float(result["lstm_improvement_percent"])
        )

        db.add(model_result)

        linear_predictions = result["linear_regression"]["predictions"]
        lstm_predictions = result["lstm"]["predictions"]

        prediction_objects = []

        # Save prediction rows
        for index, linear_row in enumerate(linear_predictions):

            lstm_row = lstm_predictions[index]

            prediction_objects.append(
                Prediction(
                    experiment_run_id=experiment_run.id,
                    asset_symbol=symbol,
                    date=pd.to_datetime(linear_row["Date"]).date(),
                    actual_return=float(linear_row["Actual_Return"]),
                    linear_regression_prediction=float(linear_row["Linear_Regression_Predicted_Return"]),
                    lstm_prediction=float(lstm_row["LSTM_Predicted_Return"])
                )
            )

        db.bulk_save_objects(prediction_objects)
        db.commit()

        return experiment_run.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Retrieve latest saved model results
def get_model_results_from_postgres():

    db = SessionLocal()

    try:
        rows = (
            db.query(ModelResult, ExperimentRun)
            .join(ExperimentRun, ModelResult.experiment_run_id == ExperimentRun.id)
            .order_by(ExperimentRun.created_at.desc())
            .all()
        )

        results = []
        seen_keys = set()

        for model_result, run in rows:

            unique_key = (
                model_result.asset_symbol,
                run.source,
                run.test_mode,
                str(run.evaluation_start),
                str(run.evaluation_end)
            )

            # Keep only newest result for identical setup
            if unique_key in seen_keys:
                continue

            seen_keys.add(unique_key)

            results.append({
                "Run_Time": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Asset": model_result.asset_symbol,
                "Source": run.source,
                "Test_Mode": run.test_mode,
                "Research_Start": "2009-01-01",
                "Evaluation_Start": str(run.evaluation_start),
                "Evaluation_End": str(run.evaluation_end),
                "Lookback_Days": run.lookback_days,
                "Linear_Regression_RMSE": model_result.linear_regression_rmse,
                "LSTM_RMSE": model_result.lstm_rmse,
                "Best_Model": model_result.best_model,
                "LSTM_Improvement_%": model_result.lstm_improvement_percent
            })

            # Limit returned rows
            if len(results) >= 15:
                break

        return results

    finally:
        db.close()
