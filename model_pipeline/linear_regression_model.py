import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import math


DEFAULT_EVALUATION_START = "2010-02-02"
DEFAULT_EVALUATION_END = "2010-05-03"


def split_train_test_data(
    df: pd.DataFrame,
    test_mode: str = "original",
    evaluation_start: str = DEFAULT_EVALUATION_START,
    evaluation_end: str = DEFAULT_EVALUATION_END,
    test_rows: int = 160
):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    evaluation_start_date = pd.to_datetime(evaluation_start)
    evaluation_end_date = pd.to_datetime(evaluation_end)

    if test_mode == "original":
        train_df = df[df["Date"] < evaluation_start_date]

        test_df = df[
            (df["Date"] >= evaluation_start_date) &
            (df["Date"] <= evaluation_end_date)
        ]

    elif test_mode == "last_160":
        train_df = df[df["Date"] < evaluation_start_date]

        future_df = df[df["Date"] >= evaluation_start_date]

        if len(future_df) < 160:
            raise ValueError("Not enough future historical rows after the selected start date for a 160-day test.")

        test_df = future_df.head(160)

    elif test_mode == "last_365":
        train_df = df[df["Date"] < evaluation_start_date]

        future_df = df[df["Date"] >= evaluation_start_date]

        if len(future_df) < 365:
            raise ValueError("Not enough future historical rows after the selected start date for a 365-day test.")

        test_df = future_df.head(365)

    elif test_mode == "custom":
        train_df = df[df["Date"] < evaluation_start_date]

        test_df = df[
            (df["Date"] >= evaluation_start_date) &
            (df["Date"] <= evaluation_end_date)
        ]

    else:
        train_df = df[df["Date"] < evaluation_start_date]

        future_df = df[df["Date"] >= evaluation_start_date]

        if len(future_df) < test_rows:
            raise ValueError(f"Not enough future historical rows after the selected start date for a {test_rows}-row test.")

        test_df = future_df.head(test_rows)

    return train_df, test_df


def run_linear_regression_model(
    df: pd.DataFrame,
    lag_days: int = 30,
    test_mode: str = "original",
    evaluation_start: str = DEFAULT_EVALUATION_START,
    evaluation_end: str = DEFAULT_EVALUATION_END,
    test_rows: int = 160
) -> dict:

    feature_columns = [f"Return_lag_{lag}" for lag in range(1, lag_days + 1)]

    train_df, test_df = split_train_test_data(
        df=df,
        test_mode=test_mode,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        test_rows=test_rows
    )

    if train_df.empty:
        raise ValueError("Training data is empty. Check the selected test period.")

    if test_df.empty:
        raise ValueError("Testing data is empty. Check the selected test period.")

    X_train = train_df[feature_columns]
    y_train = train_df["Return"]

    X_test = test_df[feature_columns]
    y_test = test_df["Return"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    predictions = model.predict(X_test_scaled)

    mse = mean_squared_error(y_test, predictions)
    rmse = math.sqrt(mse)

    prediction_rows = []

    for index, prediction in enumerate(predictions):
        row = test_df.iloc[index]

        prediction_rows.append({
            "Date": str(row["Date"].date()),
            "Actual_Return": float(row["Return"]),
            "Linear_Regression_Predicted_Return": float(prediction)
        })

    return {
        "rmse": float(rmse),
        "average_prediction": float(sum(predictions) / len(predictions)),
        "best_prediction": float(max(predictions)),
        "worst_prediction": float(min(predictions)),
        "positive_days": len([value for value in predictions if value > 0]),
        "negative_days": len([value for value in predictions if value < 0]),
        "test_rows": len(test_df),
        "predictions": prediction_rows
    }