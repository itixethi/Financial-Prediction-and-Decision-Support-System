# Financial Prediction and Decision Support System

# Financial Prediction and Decision Support System

A web-based financial analytics and decision support system developed to compare machine-learning approaches for predicting stock and ETF returns. The application compares Linear Regression and Long Short-Term Memory (LSTM) models and presents their performance through an interactive financial analytics interface.

## Project Overview

The project investigates the application of machine learning to financial market prediction by comparing **Linear Regression (LR)** and **Long Short-Term Memory (LSTM)** models.

The system began as a series of experimental Jupyter notebooks for financial data preparation, feature engineering, model training and evaluation. It was subsequently developed into a complete FastAPI web application backed by PostgreSQL.

The application allows financial assets to be analysed across defined evaluation periods, compares model performance using Root Mean Squared Error (RMSE), stores experiment results and predictions, and presents the results through interactive visualisations.

## Key Features

* Stock and ETF analysis
* Linear Regression prediction model
* LSTM neural network prediction model
* 30day return-lag feature engineering
* RMSE model evaluation
* Automatic identification of the better performing model
* Actual versus predicted return visualisation
* Historical and recent market data analysis
* Asset search and selection
* Model comparison
* Asset comparison
* Dynamic asset return correlation analysis
* Interactive correlation heatmap
* PostgreSQL experiment persistence
* Historical prediction storage
* Recent/live market-price retrieval
* Financial analytics dashboard
* Firebase authentication infrastructure

## Core Research Assets

The original experiments focus on five assets:

### Stocks

* AAPL — Apple
* AMZN — Amazon
* MSFT — Microsoft

### ETFs

* SPY — SPDR S&P 500 ETF
* QQQ — Invesco QQQ ETF

The application architecture also supports analysis of additional stocks and ETFs available through the configured datasets.

## Historical Dataset

The primary historical dataset used is the
**Stock Market Dataset by Oleh Onyshchak (2020)**, obtained through Kaggle.

**Dataset citation:**

Onyshchak, O. (2020). *Stock Market Dataset*. Kaggle.
DOI: 10.34740/KAGGLE/DSV/1054465.

The Kaggle dataset is distributed under the CC0: Public Domain licence.
According to the dataset documentation, the historical market data was
originally retrieved from Yahoo Finance using the `yfinance` Python package.

The primary research experiments in this project use:

- AAPL — Apple
- AMZN — Amazon
- MSFT — Microsoft
- SPY — SPDR S&P 500 ETF
- QQQ — Invesco QQQ ETF

The original dataset is not distributed with this repository.
Users wishing to reproduce the experiments should obtain the dataset
from its original Kaggle source.

## Feature Engineering

The prediction pipeline models financial **returns rather than raw stock prices**.

A 30-day lookback window is generated for the Linear Regression modelling process using lagged return features:

```text
Return_lag_1
Return_lag_2
...
Return_lag_30
```

This allows previous market behaviour to be used as input for predicting subsequent returns.

The modelling pipeline maintains consistent preprocessing and evaluation periods to support meaningful comparison between Linear Regression and LSTM results.

## Machine Learning Models

### Linear Regression

Linear Regression provides the statistical baseline model.

Historical lagged-return features are used to estimate subsequent financial returns.

### LSTM

A Long Short-Term Memory neural network is used as the deep learning model.

LSTM networks are designed for sequential data and provide an alternative approach for learning temporal patterns from sequences of historical financial returns.

## Model Evaluation

Model performance is primarily evaluated using **Root Mean Squared Error (RMSE)**.

For each experiment, the application records the performance of both models and determines which achieved the lower prediction error.

The Compare Models interface presents:

* Asset
* Evaluation period
* Linear Regression RMSE
* LSTM RMSE
* Best performing model

This makes the experimental period visible alongside the performance result.

## Data Sources

The system supports different financial data contexts.

### Kaggle Historical Data

Used for the primary experiments and reproducible historical model evaluation.

### Recent Market Data

Recent financial data can also be retrieved using `yfinance`, allowing the same modelling architecture to be evaluated against more recent market behaviour.

Source information and evaluation periods are retained so historical and recent experiments can be distinguished.

## PostgreSQL Database

PostgreSQL provides the persistence layer for the application.

The database architecture stores information including:

* Assets
* Historical prices
* Experiment runs
* Model results
* Predictions
* Recent market price information

Experiment metadata allows results to be associated with their asset, source, test mode and evaluation period.

The database retains experiment history while the user interface can present the most relevant recent results without displaying unnecessary duplicates.

## Application Interfaces

### Dashboard

The main dashboard provides access to financial analysis and model execution.

Users can select an asset, data source and evaluation period before running the prediction pipeline.

Results include model RMSE values, model comparisons and prediction visualisations.

### Model Results

Displays stored results produced by previous model experiments.

### Compare Models

Provides direct comparison between Linear Regression and LSTM performance for an asset, including the evaluation dates and best performing model.

### Compare Assets

Allows compatible financial assets and their model results to be compared.

### Predictions

Displays actual and predicted return information generated by the modelling pipeline.

### Correlations

The correlation system dynamically calculates relationships between compatible recently analysed assets.

Asset returns are aligned by date before their correlations are calculated.

An interactive Plotly heatmap presents the resulting correlation matrix using a fixed scale from **-1 to +1**.

### Recent Market Data

The application can retrieve recent financial market information using `yfinance` and persist relevant information in PostgreSQL.

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pandas
* NumPy
* scikit-learn
* TensorFlow / Keras
* yfinance

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript
* Jinja2
* Chart.js
* Plotly

### Authentication

* Firebase Authentication
* Google token validation

## JavaScript

JavaScript is used on the client side for application interactivity.

Its responsibilities include:

* communicating with FastAPI API endpoints
* initiating analysis requests
* updating dashboard components
* managing selected analysis options
* rendering and controlling interactive visualisations
* maintaining relevant browser side state
* Firebase authentication interaction

Backend processing, machine learning execution and database communication are implemented in Python using FastAPI.

## Project Structure

```text
Finance Prediction/
│
├── main.py
│
├── controllers/
│   ├── analysis.py
│   ├── assets.py
│   ├── compare_assets.py
│   ├── compare_models.py
│   ├── correlations.py
│   ├── dashboard.py
│   ├── live_market.py
│   ├── login.py
│   ├── model_results.py
│   └── predictions.py
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   ├── db_storage.py
│   └── models.py
│
├── firebase/
│   └── helpers.py
│
├── helpers/
│   ├── finance_helpers.py
│   ├── live_data_helpers.py
│   └── result_storage.py
│
├── model_pipeline/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── linear_regression_model.py
│   ├── lstm_model.py
│   └── run_pipeline.py
│
├── scripts/
│   ├── create_tables.py
│   ├── import_historical_assets.py
│   └── import_historical_to_postgres.py
│
├── static/
│   ├── compare-state.js
│   ├── finance-dashboard.js
│   ├── firebase-login.js
│   ├── menu-state.js
│   └── styles.css
│
├── templates/
│   ├── abstracts/
│   ├── asset_detail.html
│   ├── assets.html
│   ├── compare_assets.html
│   ├── compare_models.html
│   ├── correlations.html
│   ├── dashboard.html
│   ├── index.html
│   ├── live_market.html
│   ├── login.html
│   ├── model_results.html
│   └── predictions.html
│
├── data/
│   ├── generated_model_results.csv
│   └── generated_predictions.csv
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The `__init__.py` files identify directories such as `database` and `model_pipeline` as Python packages and support organised imports between application components.

## Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment

```bash
python3 -m venv env
```

Activate it on macOS/Linux:

```bash
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file based on `.env.example`.

For example:

```text
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/finance_prediction_db
```

### 5. Start the application

```bash
uvicorn main:app --reload
```

The development application is then available at:

```
http://127.0.0.1:8000
```

## Security

Sensitive configuration is intentionally excluded from Git.

The `.gitignore` configuration prevents files such as `.env`, virtual environments, Python cache files and private credentials from being committed.

## Current Development

The main financial prediction and decision support functionality has been implemented.

Further development includes completion/refinement of:

* financial news integration
* authenticated user functionality
* guest user functionality
* access control behaviour
* final interface refinements
* dissertation documentation

### Recent Market Data

Recent market information is retrieved programmatically using the
third-party `yfinance` Python library for research and educational purposes.

`yfinance` is an independent open source project and is not affiliated with,
endorsed by, or vetted by Yahoo. Market data obtained through the library
remains subject to the applicable terms of the original data provider.

The recent market functionality in this project is provided for educational
and research purposes and is not intended to provide investment advice.

## Context

## Academic Context

This project was developed as an MSc dissertation project investigating the application and comparative performance of machine learning approaches for financial return prediction.

The system demonstrates the integration of financial data processing, feature engineering, statistical modelling, deep learning, model evaluation, database management, backend web development and interactive data visualisation within a unified decision support system.

The project is intended for research and educational purposes and should not be interpreted as financial or investment advice.

## Author

Osabohien Igiehon

MSc Big Data Management and Analytics  