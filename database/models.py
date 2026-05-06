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


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True, index=True)
    asset_symbol = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    close = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id = Column(Integer, primary_key=True, index=True)
    asset_symbol = Column(String, ForeignKey("assets.symbol"), index=True, nullable=False)

    source = Column(String, default="kaggle")
    test_mode = Column(String, nullable=False)
    evaluation_start = Column(Date, nullable=False)
    evaluation_end = Column(Date, nullable=False)
    lookback_days = Column(Integer, default=30)

    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="experiment_runs")
    model_result = relationship("ModelResult", back_populates="experiment_run", uselist=False)
    predictions = relationship("Prediction", back_populates="experiment_run")


class ModelResult(Base):
    __tablename__ = "model_results"

    id = Column(Integer, primary_key=True, index=True)
    experiment_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=False)

    asset_symbol = Column(String, index=True, nullable=False)
    linear_regression_rmse = Column(Float, nullable=False)
    lstm_rmse = Column(Float, nullable=False)
    best_model = Column(String, nullable=False)
    lstm_improvement_percent = Column(Float, nullable=True)

    experiment_run = relationship("ExperimentRun", back_populates="model_result")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    experiment_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=False)

    asset_symbol = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    actual_return = Column(Float, nullable=True)
    linear_regression_prediction = Column(Float, nullable=True)
    lstm_prediction = Column(Float, nullable=True)

    experiment_run = relationship("ExperimentRun", back_populates="predictions")


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)

    asset_1 = Column(String, nullable=False)
    asset_2 = Column(String, nullable=False)
    source = Column(String, default="kaggle")
    test_mode = Column(String, nullable=False)
    evaluation_start = Column(Date, nullable=False)
    evaluation_end = Column(Date, nullable=False)
    interpretation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
