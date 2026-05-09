from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    asset_type = Column(String, nullable=True)
    source = Column(String, default="kaggle")
    description = Column(Text, nullable=True)

    # Marks the original dissertation baseline assets:
    # AAPL, AMZN, MSFT, SPY, QQQ
    research_group = Column(String, default="extended_historical")

    experiment_runs = relationship("ExperimentRun", back_populates="asset")

# Stores historical asset price data imported from CSV datasets
class HistoricalPrice(Base):

    __tablename__ = "historical_prices"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Asset identifier (AAPL, MSFT, SPY etc.)
    asset_symbol = Column(String, index=True, nullable=False)

    # Historical trading date
    date = Column(Date, index=True, nullable=False)

    # Standard closing price
    close = Column(Float, nullable=False)

    # Adjusted closing price
    adj_close = Column(Float, nullable=True)

    # Trading volume
    volume = Column(Float, nullable=True)


# Stores metadata for each model experiment/test run
class ExperimentRun(Base):

    __tablename__ = "experiment_runs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Linked asset symbol
    asset_symbol = Column(String, ForeignKey("assets.symbol"), index=True, nullable=False)

    # Dataset source
    source = Column(String, default="kaggle")

    # Test mode used during analysis
    test_mode = Column(String, nullable=False)

    # Evaluation date range
    evaluation_start = Column(Date, nullable=False)
    evaluation_end = Column(Date, nullable=False)

    # Number of lookback days used for training
    lookback_days = Column(Integer, default=30)

    # Timestamp for experiment creation
    created_at = Column(DateTime, default=datetime.utcnow)

    # Table relationships
    asset = relationship("Asset", back_populates="experiment_runs")
    model_result = relationship("ModelResult", back_populates="experiment_run", uselist=False)
    predictions = relationship("Prediction", back_populates="experiment_run")


# Stores model evaluation metrics
class ModelResult(Base):

    __tablename__ = "model_results"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Linked experiment run
    experiment_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=False)

    # Asset symbol
    asset_symbol = Column(String, index=True, nullable=False)

    # Model performance metrics
    linear_regression_rmse = Column(Float, nullable=False)
    lstm_rmse = Column(Float, nullable=False)

    # Best performing model
    best_model = Column(String, nullable=False)

    # Percentage improvement from LSTM
    lstm_improvement_percent = Column(Float, nullable=True)

    # Relationship back to experiment run
    experiment_run = relationship("ExperimentRun", back_populates="model_result")


# Stores prediction outputs for each experiment run
class Prediction(Base):

    __tablename__ = "predictions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Linked experiment run
    experiment_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=False)

    # Asset symbol
    asset_symbol = Column(String, index=True, nullable=False)

    # Prediction date
    date = Column(Date, index=True, nullable=False)

    # Actual and predicted returns
    actual_return = Column(Float, nullable=True)
    linear_regression_prediction = Column(Float, nullable=True)
    lstm_prediction = Column(Float, nullable=True)

    # Relationship back to experiment run
    experiment_run = relationship("ExperimentRun", back_populates="predictions")


# Stores saved asset comparison results
class Comparison(Base):

    __tablename__ = "comparisons"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Compared assets
    asset_1 = Column(String, nullable=False)
    asset_2 = Column(String, nullable=False)

    # Comparison configuration
    source = Column(String, default="kaggle")
    test_mode = Column(String, nullable=False)

    # Evaluation period
    evaluation_start = Column(Date, nullable=False)
    evaluation_end = Column(Date, nullable=False)

    # Generated comparison interpretation
    interpretation = Column(Text, nullable=True)

    # Timestamp for comparison creation
    created_at = Column(DateTime, default=datetime.utcnow)


# Stores live market data retrieved from yfinance
class LiveMarketPrice(Base):

    __tablename__ = "live_market_prices"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Asset symbol
    asset_symbol = Column(String, index=True, nullable=False)

    # Market date
    date = Column(Date, index=True, nullable=False)

    # Live closing price
    close = Column(Float, nullable=False)

    # Trading volume
    volume = Column(Float, nullable=True)

    # Data source
    source = Column(String, default="yfinance")

    # Timestamp for record creation
    created_at = Column(DateTime, default=datetime.utcnow)
