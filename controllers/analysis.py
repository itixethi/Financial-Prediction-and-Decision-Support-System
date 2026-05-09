from fastapi import Request
from fastapi.responses import JSONResponse

from model_pipeline.run_pipeline import run_analysis_pipeline
from model_pipeline.data_loader import load_asset_price_data

from helpers.result_storage import save_analysis_result

from database.db_storage import save_analysis_result_to_postgres, save_live_market_data_to_postgres

async def apiRunAnalysis(asset: str, request: Request):
    try:
        asset = asset.upper().strip()

        body = await request.json()

        source = body.get("source", "kaggle").strip()
        test_mode = body.get("test_mode", "original").strip()
        evaluation_start = body.get("evaluation_start", "2010-02-02").strip()
        evaluation_end = body.get("evaluation_end", "2010-05-03").strip()

        result = run_analysis_pipeline(
            asset,
            source=source,
            test_mode=test_mode,
            evaluation_start=evaluation_start,
            evaluation_end=evaluation_end
        )

        if source == "live":
            live_df = load_asset_price_data(asset, source="live")
            save_live_market_data_to_postgres(asset, live_df)

        # CSV backup / existing project storage
        save_analysis_result(result)

        # PostgreSQL main storage
        save_analysis_result_to_postgres(result)
        
        return result

    except Exception as e:
        return {"asset": asset.upper(), "status": "error", "message": str(e)}