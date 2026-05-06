import math
import random
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

from model_pipeline.linear_regression_model import split_train_test_data

# Dissertation evaluation window
EVALUATION_START = "2010-02-02"
EVALUATION_END = "2010-05-03"


# This function trains and evaluates the LSTM model using the same research mode window.
# It uses Return_lag_1 to Return_lag_30 as sequence input.
def run_lstm_model(
    df: pd.DataFrame,
    lag_days: int = 30,
    test_mode: str = "original",
    evaluation_start: str = "2010-02-02",
    evaluation_end: str = "2010-05-03",
    test_rows: int = 160
) -> dict:
    # Set random seeds to make LSTM results more stable between runs
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)

    # Clear previous TensorFlow model/session
    tf.keras.backend.clear_session()

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    feature_columns = [f"Return_lag_{lag}" for lag in range(1, lag_days + 1)]

    train_df, test_df = split_train_test_data(
        df=df,
        test_mode=test_mode,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        test_rows=test_rows
    )

    if train_df.empty:
        raise ValueError("LSTM training data is empty. Check the 2009 buffer period.")

    if test_df.empty:
        raise ValueError("LSTM testing data is empty. Check the fixed evaluation window.")

    X_train = train_df[feature_columns].values
    y_train = train_df["Return"].values

    X_test = test_df[feature_columns].values
    y_test = test_df["Return"].values

    # MinMaxScaler follows the LSTM setup used in the dissertation work
    scaler = MinMaxScaler(feature_range=(-1, 1))

    # Fit only on training features to avoid data leakage
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Reshape data for LSTM:
    # samples, time_steps, features
    # Here each row has 30 lagged returns treated as a 30 step sequence with 1 feature.
    X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], lag_days, 1))
    X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], lag_days, 1))

    # Build LSTM model
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(lag_days, 1)))
    model.add(tf.keras.layers.LSTM(50))
    model.add(tf.keras.layers.Dropout(0.2))
    model.add(tf.keras.layers.Dense(1))

    model.compile(optimizer="adam", loss="mse")

    # Train model
    model.fit(
        X_train_lstm,
        y_train,
        epochs=20,
        batch_size=32,
        verbose=0
    )

    # Predict returns
    predictions = model.predict(X_test_lstm, verbose=0).flatten()

    # Calculate RMSE
    mse = mean_squared_error(y_test, predictions)
    rmse = math.sqrt(mse)

    prediction_rows = []

    for index, prediction in enumerate(predictions):
        row = test_df.iloc[index]

        prediction_rows.append({
            "Date": str(row["Date"].date()),
            "Actual_Return": float(row["Return"]),
            "LSTM_Predicted_Return": float(prediction)
        })

    average_prediction = float(np.mean(predictions))
    best_prediction = float(np.max(predictions))
    worst_prediction = float(np.min(predictions))

    positive_days = int(len([value for value in predictions if value > 0]))
    negative_days = int(len([value for value in predictions if value < 0]))

    return {
        "rmse": float(rmse),
        "average_prediction": average_prediction,
        "best_prediction": best_prediction,
        "worst_prediction": worst_prediction,
        "positive_days": positive_days,
        "negative_days": negative_days,
        "test_rows": len(test_df),
        "predictions": prediction_rows
    }