from model_pipeline.data_loader import load_asset_price_data
from model_pipeline.feature_engineering import prepare_return_features
from model_pipeline.linear_regression_model import run_linear_regression_model
from model_pipeline.lstm_model import run_lstm_model


def get_readable_test_mode(test_mode: str) -> str:
    model_labels = {
        "original": "Original dissertation window",
        "last_160": "Next 160 trading days",
        "last_365": "Next 365 trading days",
        "custom": "Custom date range"
    }
    return model_labels.get(test_mode, test_mode)

def get_readable_source_mode(source: str) -> str:
    source_labels = {
        "kaggle": "Historical Kaggle Dissertation Data",
        "live": "Recent 5-Year Live Data"
    }

    return source_labels.get(source, source)


# This is the main pipeline called by
# source="kaggle" reproduces the dissertation research setup.
# source="live" supports dynamic/live prediction.
def run_analysis_pipeline(
    symbol: str,
    source: str = "kaggle",
    test_mode: str = "original",
    evaluation_start: str = "2010-02-02",
    evaluation_end: str = "2010-05-03",
    test_rows: int = 160
) -> dict:
    raw_df = load_asset_price_data(symbol=symbol, source=source)

    model_df = prepare_return_features(raw_df, lag_days=30)

    linear_result = run_linear_regression_model(
        model_df,
        lag_days=30,
        test_mode=test_mode,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        test_rows=test_rows
    )

    lstm_result = run_lstm_model(
        model_df,
        lag_days=30,
        test_mode=test_mode,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        test_rows=test_rows
    )

    linear_rmse = linear_result["rmse"]
    lstm_rmse = lstm_result["rmse"]

    best_model = "LSTM" if lstm_rmse < linear_rmse else "Linear Regression"

    lstm_improvement_percent = ((linear_rmse - lstm_rmse) / linear_rmse) * 100

    readable_test_mode = get_readable_test_mode(test_mode)
    mode_label = get_readable_source_mode(source)
    
    return {
        "asset": symbol.upper(),
        "source": source,
        "mode_label": mode_label,
        "status": "success",
        "test_mode": test_mode,
        "readable_test_mode": readable_test_mode,
        "research_start": "2009-01-01",
        "evaluation_start": evaluation_start,
        "evaluation_end": evaluation_end,
        "lookback_days": 30,

        "linear_regression": {
            "model_used": "Linear Regression",
            "rmse": linear_result["rmse"],
            "average_prediction": linear_result["average_prediction"],
            "best_prediction": linear_result["best_prediction"],
            "worst_prediction": linear_result["worst_prediction"],
            "positive_days": linear_result["positive_days"],
            "negative_days": linear_result["negative_days"],
            "test_rows": linear_result["test_rows"],
            "predictions": linear_result["predictions"]
        },

        "lstm": {
            "model_used": "LSTM",
            "rmse": lstm_result["rmse"],
            "average_prediction": lstm_result["average_prediction"],
            "best_prediction": lstm_result["best_prediction"],
            "worst_prediction": lstm_result["worst_prediction"],
            "positive_days": lstm_result["positive_days"],
            "negative_days": lstm_result["negative_days"],
            "test_rows": lstm_result["test_rows"],
            "predictions": lstm_result["predictions"]
        },

        "best_model": best_model,
        "lstm_improvement_percent": lstm_improvement_percent,
        "message": f"{readable_test_mode} Linear Regression and LSTM analysis completed for {symbol.upper()}."
    }