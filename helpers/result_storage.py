import os
import pandas as pd
from datetime import datetime

MODEL_RESULTS_PATH = "data/generated_model_results.csv"
PREDICTIONS_PATH = "data/generated_predictions.csv"


# Save model summary results from a completed analysis run
def save_model_result(result: dict):
    model_row = {
        "Run_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Asset": result["asset"],
        "Source": result["source"],
        "Test_Mode": result["test_mode"],
        "Research_Start": result["research_start"],
        "Evaluation_Start": result["evaluation_start"],
        "Evaluation_End": result["evaluation_end"],
        "Lookback_Days": result["lookback_days"],
        "Linear_Regression_RMSE": result["linear_regression"]["rmse"],
        "LSTM_RMSE": result["lstm"]["rmse"],
        "Best_Model": result["best_model"],
        "LSTM_Improvement_%": result["lstm_improvement_percent"]
    }

    new_df = pd.DataFrame([model_row])

    if os.path.exists(MODEL_RESULTS_PATH):
        existing_df = pd.read_csv(MODEL_RESULTS_PATH)

        # Remove old result for the same asset/source so latest run replaces it
        existing_df = existing_df[
            ~(
                (existing_df["Asset"] == result["asset"]) &
                (existing_df["Source"] == result["source"])
            )
        ]

        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    final_df.to_csv(MODEL_RESULTS_PATH, index=False)


# Save prediction rows from both Linear Regression and LSTM
def save_predictions(result: dict):
    prediction_rows = []

    linear_predictions = result["linear_regression"]["predictions"]
    lstm_predictions = result["lstm"]["predictions"]

    for index, linear_row in enumerate(linear_predictions):
        lstm_row = lstm_predictions[index]

        prediction_rows.append({
            "Run_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Asset": result["asset"],
            "Source": result["source"],
            "Date": linear_row["Date"],
            "Actual_Return": linear_row["Actual_Return"],
            "Linear_Regression_Predicted_Return": linear_row["Linear_Regression_Predicted_Return"],
            "LSTM_Predicted_Return": lstm_row["LSTM_Predicted_Return"]
        })

    new_df = pd.DataFrame(prediction_rows)

    if os.path.exists(PREDICTIONS_PATH):
        existing_df = pd.read_csv(PREDICTIONS_PATH)

        # Remove old prediction rows for the same asset/source
        existing_df = existing_df[
            ~(
                (existing_df["Asset"] == result["asset"]) &
                (existing_df["Source"] == result["source"])
            )
        ]

        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    final_df.to_csv(PREDICTIONS_PATH, index=False)


# Save all generated outputs
def save_analysis_result(result: dict):
    save_model_result(result)
    save_predictions(result)