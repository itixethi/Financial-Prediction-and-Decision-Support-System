async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}`);
  }

  return await response.json();
}

let rmseChartInstance = null;
let predictionChartInstance = null;

function getReadableTestMode(testMode) {
  const labels = {
    original: "Original dissertation-window",
    last_160: "Next 160 trading days",
    last_365: "Next 365 trading days",
    custom: "Custom date range"
  };

  return labels[testMode] || testMode;
}

function buildDashboardUrl(asset, testMode, evaluationStart, evaluationEnd, source = "kaggle") {
  const params = new URLSearchParams();

  params.set("asset", asset);
  params.set("source", source);
  params.set("test_mode", testMode);
  params.set("evaluation_start", evaluationStart);
  params.set("evaluation_end", evaluationEnd);

  return `/dashboard?${params.toString()}`;
}

function syncDashboardUrlFromStorage() {
  if (!window.location.pathname.includes("/dashboard")) {
    return false;
  }

  const params = new URLSearchParams(window.location.search);

  if (params.has("asset")) {
    return false;
  }

  const savedAsset = localStorage.getItem("loadedAsset");

  if (!savedAsset) {
    return false;
  }

  const savedTestMode = localStorage.getItem("testMode") || "original";
  const savedEvaluationStart = localStorage.getItem("evaluationStart") || "2010-02-02";
  const savedEvaluationEnd = localStorage.getItem("evaluationEnd") || "2010-05-03";
  const savedSource = localStorage.getItem("source") || "kaggle";


  window.location.replace(
    buildDashboardUrl(
      savedAsset,
      savedTestMode,
      savedEvaluationStart,
      savedEvaluationEnd,
      savedSource
    )
  );

  return true;
}

function renderRmseChart(chartElement, selectedAsset, linearRmse, lstmRmse) {
  if (!chartElement) {
    return;
  }

  if (rmseChartInstance) {
    rmseChartInstance.destroy();
  }

  rmseChartInstance = new Chart(chartElement, {
    type: "bar",
    data: {
      labels: ["Linear Regression", "LSTM"],
      datasets: [
        {
          label: `${selectedAsset} RMSE`,
          data: [linearRmse, lstmRmse]
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: `${selectedAsset} Linear Regression vs LSTM RMSE`
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

async function drawRmseChart() {
  const chartElement = document.getElementById("rmseChart");

  if (!chartElement) {
    return;
  }

  const selectedAsset = chartElement.dataset.asset;
  const modelResults = await fetchJson("/api/model-results");

  const result = modelResults.find(
    (item) => item.Asset.toUpperCase() === selectedAsset.toUpperCase()
  );

  if (!result) {
    return;
  }

  renderRmseChart(
    chartElement,
    selectedAsset,
    result.Linear_Regression_RMSE,
    result.LSTM_RMSE
  );
}

function renderPredictionChart(chartElement, selectedAsset, predictions) {
  if (!chartElement) {
    return;
  }

  if (predictionChartInstance) {
    predictionChartInstance.destroy();
  }

  if (!predictions || predictions.length === 0) {
    return;
  }

  const dates = predictions.map((row) => row.Date);
  const actualReturns = predictions.map((row) => row.Actual_Return);
  const linearPredictions = predictions.map(
    (row) => row.Linear_Regression_Predicted_Return
  );
  const lstmPredictions = predictions.map(
    (row) => row.LSTM_Predicted_Return
  );

  predictionChartInstance = new Chart(chartElement, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: "Actual Return",
          data: actualReturns,
          tension: 0.2
        },
        {
          label: "Linear Regression Prediction",
          data: linearPredictions,
          tension: 0.2
        },
        {
          label: "LSTM Prediction",
          data: lstmPredictions,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: `${selectedAsset} Actual vs Predicted Returns`
        }
      },
      scales: {
        y: {
          suggestedMin: -0.05,
          suggestedMax: 0.05
        }
      }
    }
  });
}

async function drawPredictionChart() {
  const chartElement = document.getElementById("predictionChart");

  if (!chartElement) {
    return;
  }

  const selectedAsset = chartElement.dataset.asset;
  const predictions = await fetchJson(`/api/predictions/${selectedAsset}`);

  renderPredictionChart(chartElement, selectedAsset, predictions);
}

function setupRunAnalysisButton() {
  const runButton = document.getElementById("runAnalysisButton");
  const messageBox = document.getElementById("analysisMessage");

  if (!runButton || !messageBox) {
    return;
  }

  runButton.addEventListener("click", async () => {
    const selectedAsset = runButton.dataset.asset;

    const dataSourceSelect = document.getElementById("dataSourceSelect");
    const testModeSelect = document.getElementById("testModeSelect");
    const evaluationStartInput = document.getElementById("evaluationStartInput");
    const evaluationEndInput = document.getElementById("evaluationEndInput");

    const source = dataSourceSelect ? dataSourceSelect.value : "kaggle";
    const testMode = testModeSelect ? testModeSelect.value : "original";
    const readableTestMode = getReadableTestMode(testMode);
    const evaluationStart = evaluationStartInput ? evaluationStartInput.value : "2010-02-02";
    const evaluationEnd = evaluationEndInput ? evaluationEndInput.value : "2010-05-03";

    messageBox.hidden = false;
    messageBox.className = "alert alert-warning mt-3";
    messageBox.textContent = `Running ${readableTestMode} Linear Regression and LSTM analysis for ${selectedAsset}...`;

    try {
      const response = await fetch(`/api/run-analysis/${selectedAsset}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          source: source,
          test_mode: testMode,
          evaluation_start: evaluationStart,
          evaluation_end: evaluationEnd
        })
      });

      const result = await response.json();

      if (result.status === "success") {
        localStorage.setItem("loadedAsset", selectedAsset);
        localStorage.setItem("selectedAsset", selectedAsset);
        localStorage.setItem("lastAnalysedAsset", selectedAsset);
        localStorage.setItem("testMode", testMode);
        localStorage.setItem("evaluationStart", evaluationStart);
        localStorage.setItem("evaluationEnd", evaluationEnd);
        localStorage.setItem("source", source);

        const linearRmseCard = document.getElementById("linearRmseCard");
        const lstmRmseCard = document.getElementById("lstmRmseCard");
        const bestModelCard = document.getElementById("bestModelCard");
        const lstmImprovementCard = document.getElementById("lstmImprovementCard");

        if (linearRmseCard) {
          linearRmseCard.textContent = result.linear_regression.rmse.toFixed(6);
        }

        if (lstmRmseCard) {
          lstmRmseCard.textContent = result.lstm.rmse.toFixed(6);
        }

        if (bestModelCard) {
          bestModelCard.textContent = result.best_model;
        }

        if (lstmImprovementCard) {
          lstmImprovementCard.textContent = `${result.lstm_improvement_percent.toFixed(2)}%`;
        }

        const rmseChartElement = document.getElementById("rmseChart");

        renderRmseChart(
          rmseChartElement,
          selectedAsset,
          result.linear_regression.rmse,
          result.lstm.rmse
        );

        const predictionChartElement = document.getElementById("predictionChart");

        renderPredictionChart(
          predictionChartElement,
          selectedAsset,
          result.linear_regression.predictions.map((linearRow, index) => {
            return {
              Date: linearRow.Date,
              Actual_Return: linearRow.Actual_Return,
              Linear_Regression_Predicted_Return: linearRow.Linear_Regression_Predicted_Return,
              LSTM_Predicted_Return: result.lstm.predictions[index].LSTM_Predicted_Return
            };
          })
        );

        window.history.replaceState(
          {},
          "",
          buildDashboardUrl(
            selectedAsset,
            testMode,
            evaluationStart,
            evaluationEnd,
            source
          )
        );

        const menuDashboardLink = document.getElementById("menuDashboardLink");
        
        if (menuDashboardLink) {
            menuDashboardLink.href = buildDashboardUrl(
                selectedAsset,
                testMode,
                evaluationStart,
                evaluationEnd,
                source
            );
        }

        const predictionPageLink = document.getElementById("predictionPageLink");

        if (predictionPageLink) {
          predictionPageLink.href = `/predictions/${selectedAsset}`;
        }

        const menuPredictionLink = document.getElementById("menuPredictionLink");

        if (menuPredictionLink) {
          menuPredictionLink.href = `/predictions/${selectedAsset}`;
        }

        messageBox.className = "alert alert-success mt-3";
        messageBox.innerHTML = `
          <strong>${result.message}</strong><br><br>
          <strong>Dataset Source:</strong> ${result.source}<br>
          <strong>Mode:</strong> ${result.mode_label || "Historical Kaggle Dissertation Data"}<br>
          <strong>Test Period Mode:</strong> ${result.readable_test_mode || readableTestMode}<br>
          <strong>Evaluation Window:</strong> ${result.evaluation_start} to ${result.evaluation_end}<br>
          <strong>Test Rows:</strong> ${result.linear_regression.test_rows}<br><br>

          <strong>Linear Regression RMSE:</strong> ${result.linear_regression.rmse.toFixed(6)}<br>
          <strong>LSTM RMSE:</strong> ${result.lstm.rmse.toFixed(6)}<br>
          <strong>Best Model:</strong> ${result.best_model}<br>
          <strong>LSTM Improvement:</strong> ${result.lstm_improvement_percent.toFixed(2)}%
        `;
      } else {
        messageBox.className = "alert alert-danger mt-3";
        messageBox.textContent = result.message;
      }

    } catch (error) {
      messageBox.className = "alert alert-danger mt-3";
      messageBox.textContent = "Analysis request failed. Please check the server.";
      console.error(error);
    }
  });
}

async function drawAllModelResultsChart() {
  const chartElement = document.getElementById("allModelResultsChart");

  if (!chartElement) {
    return;
  }

  const modelResults = await fetchJson("/api/model-results");

  const assets = modelResults.map((row) => {return `${row.Asset} (${row.Source}, ${row.Evaluation_Start} - ${row.Evaluation_End})`;});
  const linearRmse = modelResults.map((row) => row.Linear_Regression_RMSE);
  const lstmRmse = modelResults.map((row) => row.LSTM_RMSE);

  new Chart(chartElement, {
    type: "bar",
    data: {
      labels: assets,
      datasets: [
        {
          label: "Linear Regression RMSE",
          data: linearRmse
        },
        {
          label: "LSTM RMSE",
          data: lstmRmse
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: "Linear Regression vs LSTM RMSE Across Assets"
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

async function drawCompareAssetsRmseChart() {
  const chartElement = document.getElementById("compareAssetsRmseChart");

  if (!chartElement) {
    return;
  }

  const assetOne = chartElement.dataset.assetOne;
  const assetTwo = chartElement.dataset.assetTwo;

  const modelResults = await fetchJson("/api/model-results");

  const assetOneResult = modelResults.find(
    (row) => row.Asset.toUpperCase() === assetOne.toUpperCase()
  );

  const assetTwoResult = modelResults.find(
    (row) => row.Asset.toUpperCase() === assetTwo.toUpperCase()
  );

  if (!assetOneResult || !assetTwoResult) {
    return;
  }

  new Chart(chartElement, {
    type: "bar",
    data: {
      labels: [assetOne, assetTwo],
      datasets: [
        {
          label: "Linear Regression RMSE",
          data: [
            assetOneResult.Linear_Regression_RMSE,
            assetTwoResult.Linear_Regression_RMSE
          ]
        },
        {
          label: "LSTM RMSE",
          data: [
            assetOneResult.LSTM_RMSE,
            assetTwoResult.LSTM_RMSE
          ]
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: `${assetOne} vs ${assetTwo} RMSE Comparison`
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

async function drawCompareAssetsPredictionChart() {
  const chartElement = document.getElementById("compareAssetsPredictionChart");

  if (!chartElement) {
    return;
  }

  const assetOne = chartElement.dataset.assetOne;
  const assetTwo = chartElement.dataset.assetTwo;

  const assetOnePredictions = await fetchJson(`/api/predictions/${assetOne}`);
  const assetTwoPredictions = await fetchJson(`/api/predictions/${assetTwo}`);

  if (!assetOnePredictions.length || !assetTwoPredictions.length) {
    return;
  }

  const assetOneAverage =
    assetOnePredictions.reduce((total, row) => total + row.LSTM_Predicted_Return, 0) /
    assetOnePredictions.length;

  const assetTwoAverage =
    assetTwoPredictions.reduce((total, row) => total + row.LSTM_Predicted_Return, 0) /
    assetTwoPredictions.length;

  new Chart(chartElement, {
    type: "bar",
    data: {
      labels: [assetOne, assetTwo],
      datasets: [
        {
          label: "Average LSTM Predicted Return",
          data: [assetOneAverage, assetTwoAverage]
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: `${assetOne} vs ${assetTwo} Average Predicted Return`
        }
      },
      scales: {
        y: {
          suggestedMin: -0.05,
          suggestedMax: 0.05
        }
      }
    }
  });
}

async function drawCorrelationChart() {
  const heatmapElement = document.getElementById("correlationHeatmap");

  if (!heatmapElement) {
    return;
  }

  const correlationData = await fetchJson("/api/correlations");

  const labels = correlationData.labels || [];
  const matrix = correlationData.matrix || [];
  const message = correlationData.message || "No correlation data available.";

  if (!labels.length || !matrix.length) {
    heatmapElement.innerHTML = `
      <div class="alert alert-warning">
        ${message}
      </div>
    `;
    return;
  }

  const data = [
    {
      z: matrix,
      x: labels,
      y: labels,
      type: "heatmap",
      zmin: -1.0,
      zmax: 1.0,
      colorscale: [
        [0.0, "rgb(0, 0, 128)"],
        [0.25, "rgb(0, 102, 255)"],
        [0.5, "rgb(255, 255, 255)"],
        [0.75, "rgb(255, 102, 0)"],
        [1.0, "rgb(128, 0, 0)"]
      ],
      colorbar: {
        title: "Correlation",
        titleside: "right",
        thickness: 18,
        len: 0.8
      },
      hoverongaps: false,
      hovertemplate:
        "<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.4f}<extra></extra>"
    }
  ];

  const layout = {
    title: "Correlation Matrix of Asset Returns",
    margin: {
      t: 50,
      r: 40,
      b: 80,
      l: 80
    },
    xaxis: {
      title: "",
      tickangle: -45
    },
    yaxis: {
      title: "",
      autorange: "reversed"
    }
  };

  Plotly.newPlot(heatmapElement, data, layout, {
    responsive: true
  });
}

async function drawLiveMarketChart() {
  const chartElement = document.getElementById("liveMarketChart");

  if (!chartElement) {
    return;
  }

  const symbol = chartElement.dataset.symbol;
  const marketData = await fetchJson(`/api/live-market/${symbol}`);

  const priceRows = Array.isArray(marketData.price_data)
    ? marketData.price_data
    : marketData.price_data.price_data;

  if (!priceRows || priceRows.length === 0) {
    return;
  }

  const dates = priceRows.map((row) => row.date);
  const closePrices = priceRows.map((row) => row.close);

  new Chart(chartElement, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: `${symbol} Close Price`,
          data: closePrices,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        },
        title: {
          display: true,
          text: `${symbol} Recent Closing Prices`
        }
      }
    }
  });
}

function setupDashboardStatePersistence() {
  const assetInput = document.querySelector("input[name='asset']");
  const dataSourceSelect = document.getElementById("dataSourceSelect");
  const testModeSelect = document.getElementById("testModeSelect");
  const evaluationStartInput = document.getElementById("evaluationStartInput");
  const evaluationEndInput = document.getElementById("evaluationEndInput");
  const predictionPageLink = document.getElementById("predictionPageLink");
  const menuPredictionLink = document.getElementById("menuPredictionLink");
  const menuDashboardLink = document.getElementById("menuDashboardLink");
  const dashboardAssetForm = document.getElementById("dashboardAssetForm");

  const hiddenSource = document.getElementById("hiddenSource");
  const hiddenTestMode = document.getElementById("hiddenTestMode");
  const hiddenEvaluationStart = document.getElementById("hiddenEvaluationStart");
  const hiddenEvaluationEnd = document.getElementById("hiddenEvaluationEnd");

  function updateHiddenFields() {
    if (hiddenSource && dataSourceSelect) {
        hiddenSource.value = dataSourceSelect.value;
    }

    if (hiddenTestMode && testModeSelect) {
      hiddenTestMode.value = testModeSelect.value;
    }

    if (hiddenEvaluationStart && evaluationStartInput) {
      hiddenEvaluationStart.value = evaluationStartInput.value;
    }

    if (hiddenEvaluationEnd && evaluationEndInput) {
      hiddenEvaluationEnd.value = evaluationEndInput.value;
    }
  }

  function updatePredictionLinks(asset) {
    const savedAsset = localStorage.getItem("lastAnalysedAsset") || localStorage.getItem("loadedAsset") || localStorage.getItem("selectedAsset");
    const cleanAsset = asset ? asset.trim().toUpperCase() : (savedAsset || "AAPL");
    
    if (predictionPageLink) {
        predictionPageLink.href = `/predictions/${cleanAsset}`;
    }
    
    if (menuPredictionLink) {
        menuPredictionLink.href = `/predictions/${cleanAsset}`;
    }
}

  const savedSource = localStorage.getItem("source"); 
  const savedTestMode = localStorage.getItem("testMode");
  const savedEvaluationStart = localStorage.getItem("evaluationStart");
  const savedEvaluationEnd = localStorage.getItem("evaluationEnd");

  if (dataSourceSelect && savedSource) {
    dataSourceSelect.value = savedSource;
  }

  if (testModeSelect && savedTestMode) {
    testModeSelect.value = savedTestMode;
  }

  if (evaluationStartInput && savedEvaluationStart) {
    evaluationStartInput.value = savedEvaluationStart;
  }

  if (evaluationEndInput && savedEvaluationEnd) {
    evaluationEndInput.value = savedEvaluationEnd;
  }

  updateHiddenFields();

  function updateDashboardLink() {
    const savedAsset = localStorage.getItem("loadedAsset") || "AAPL";
    const savedTestMode = localStorage.getItem("testMode") || "original";
    const savedEvaluationStart = localStorage.getItem("evaluationStart") || "2010-02-02";
    const savedEvaluationEnd = localStorage.getItem("evaluationEnd") || "2010-05-03";
    const savedSource = localStorage.getItem("source") || "kaggle";
    
    if (menuDashboardLink) {
        menuDashboardLink.href = buildDashboardUrl(
            savedAsset,
            savedTestMode,
            savedEvaluationStart,
            savedEvaluationEnd,
            savedSource
        );
    }
}

updateDashboardLink();

if (assetInput) {
    updatePredictionLinks();
}
  

  if (dashboardAssetForm && assetInput) {
    dashboardAssetForm.addEventListener("submit", () => {
      const loadedAsset = assetInput.value.trim().toUpperCase();

      localStorage.setItem("loadedAsset", loadedAsset);
      localStorage.setItem("selectedAsset", loadedAsset);

      if (testModeSelect) {
        localStorage.setItem("testMode", testModeSelect.value);
      }

      if (evaluationStartInput) {
        localStorage.setItem("evaluationStart", evaluationStartInput.value);
      }

      if (evaluationEndInput) {
        localStorage.setItem("evaluationEnd", evaluationEndInput.value);
      }

      if (dataSourceSelect) {
        localStorage.setItem("source", dataSourceSelect.value);
      }

      updateHiddenFields();
      updatePredictionLinks(loadedAsset);
      updateDashboardLink();
    });
  }

  if (dataSourceSelect) {
    dataSourceSelect.addEventListener("change", () => {
      localStorage.setItem("source", dataSourceSelect.value);
      updateHiddenFields();
      updateDashboardLink();
    });
  }

  if (testModeSelect) {
    testModeSelect.addEventListener("change", () => {
      localStorage.setItem("testMode", testModeSelect.value);
      updateHiddenFields();
    });
  }

  if (evaluationStartInput) {
    evaluationStartInput.addEventListener("change", () => {
      localStorage.setItem("evaluationStart", evaluationStartInput.value);
      updateHiddenFields();
    });
  }

  if (evaluationEndInput) {
    evaluationEndInput.addEventListener("change", () => {
      localStorage.setItem("evaluationEnd", evaluationEndInput.value);
      updateHiddenFields();
    });
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const redirected = syncDashboardUrlFromStorage();

    if (redirected) {
      return;
    }

    setupDashboardStatePersistence();

    await drawRmseChart();
    await drawPredictionChart();
    await drawLiveMarketChart();
    await drawCompareAssetsRmseChart();
    await drawCompareAssetsPredictionChart();
    await drawAllModelResultsChart();
    await drawCorrelationChart();

    setupRunAnalysisButton();
  } catch (error) {
    console.error("Dashboard chart error:", error);
  }
});

