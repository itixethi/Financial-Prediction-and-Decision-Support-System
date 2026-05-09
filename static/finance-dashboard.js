// Reusable helper for fetching JSON data from API endpoints
async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}`);
  }

  return await response.json();
}

// Store active chart instances so they can be replaced safely
let rmseChartInstance = null;
let predictionChartInstance = null;


// Convert test mode keys into readable labels
function getReadableTestMode(testMode) {
  const labels = {
    original: "Original dissertation-window",
    last_160: "Next 160 trading days",
    last_365: "Next 365 trading days",
    custom: "Custom date range"
  };

  return labels[testMode] || testMode;
}


// Build dashboard URL with selected analysis filters
function buildDashboardUrl(asset, testMode, evaluationStart, evaluationEnd, source = "kaggle") {
  const params = new URLSearchParams();

  params.set("asset", asset);
  params.set("source", source);
  params.set("test_mode", testMode);
  params.set("evaluation_start", evaluationStart);
  params.set("evaluation_end", evaluationEnd);

  return `/dashboard?${params.toString()}`;
}


// Restore dashboard URL from localStorage when no asset is in the URL
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


// Render RMSE bar chart for one asset
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


// Load model results and draw selected asset RMSE chart
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


// Tender actual vs predicted returns chart
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
  const linearPredictions = predictions.map((row) => row.Linear_Regression_Predicted_Return);
  const lstmPredictions = predictions.map((row) => row.LSTM_Predicted_Return);

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


// Load prediction data and draw prediction chart
async function drawPredictionChart() {
  const chartElement = document.getElementById("predictionChart");

  if (!chartElement) {
    return;
  }

  const selectedAsset = chartElement.dataset.asset;
  const predictions = await fetchJson(`/api/predictions/${selectedAsset}`);

  renderPredictionChart(chartElement, selectedAsset, predictions);
}


// Set up analysis button and update dashboard after model run
function setupRunAnalysisButton() {
  const runButton = document.getElementById("runAnalysisButton");
  const messageBox = document.getElementById("analysisMessage");

  if (!runButton || !messageBox) {
    return;
  }

  runButton.addEventListener("click", async () => {
    const selectedAsset = runButton.dataset.asset;

    // Read selected analysis settings
    const dataSourceSelect = document.getElementById("dataSourceSelect");
    const testModeSelect = document.getElementById("testModeSelect");
    const evaluationStartInput = document.getElementById("evaluationStartInput");
    const evaluationEndInput = document.getElementById("evaluationEndInput");

    const source = dataSourceSelect ? dataSourceSelect.value : "kaggle";
    const testMode = testModeSelect ? testModeSelect.value : "original";
    const readableTestMode = getReadableTestMode(testMode);
    const evaluationStart = evaluationStartInput ? evaluationStartInput.value : "2010-02-02";
    const evaluationEnd = evaluationEndInput ? evaluationEndInput.value : "2010-05-03";

    // Show running status
    messageBox.hidden = false;
    messageBox.className = "alert alert-warning mt-3";
    messageBox.textContent = `Running ${readableTestMode} Linear Regression and LSTM analysis for ${selectedAsset}...`;

    try {
      // Run backend analysis
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
        // Persist selected analysis state
        localStorage.setItem("loadedAsset", selectedAsset);
        localStorage.setItem("selectedAsset", selectedAsset);
        localStorage.setItem("lastAnalysedAsset", selectedAsset);
        localStorage.setItem("testMode", testMode);
        localStorage.setItem("evaluationStart", evaluationStart);
        localStorage.setItem("evaluationEnd", evaluationEnd);
        localStorage.setItem("source", source);

        // Update metric cards
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

        // Refresh RMSE chart
        renderRmseChart(
          document.getElementById("rmseChart"),
          selectedAsset,
          result.linear_regression.rmse,
          result.lstm.rmse
        );

        // Refresh prediction chart
        renderPredictionChart(
          document.getElementById("predictionChart"),
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

        // Update browser URL without reloading
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

        // Update navigation links
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

        // Show success summary
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

