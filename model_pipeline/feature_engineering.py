import pandas as pd

# This function prepares the historical price data for modelling.
# It follows my dissertation setup
# uses Close price
# creates daily returns
# creates Return_lag_1 to Return_lag_30
# drops missing rows caused by return and lag creationx
def prepare_return_features(df: pd.DataFrame, lag_days: int = 30) -> pd.DataFrame:
    # Sort data by Date to make sure lag features are created in correct time order
    df = df.sort_values("Date").copy()

    # Create the target variable: daily return from Close price
    df["Return"] = df["Close"].pct_change()

    # Create lagged return features
    for lag in range(1, lag_days + 1):
        df[f"Return_lag_{lag}"] = df["Return"].shift(lag)

    # Remove rows with missing values from pct_change and lag creation
    df = df.dropna().reset_index(drop=True)

    return df