// Handle saved compare assets form state
function setupCompareAssetsState() {

  // Get compare form
  const form = document.getElementById("compareAssetsForm");

  // Stop if form does not exist
  if (!form) {
    return;
  }

  // Form inputs
  const sourceSelect = document.getElementById("compareSourceSelect");
  const assetOneInput = document.getElementById("compareAssetOneInput");
  const assetTwoInput = document.getElementById("compareAssetTwoInput");
  const testModeSelect = document.getElementById("compareTestModeSelect");
  const evaluationStartInput = document.getElementById("compareEvaluationStartInput");
  const evaluationEndInput = document.getElementById("compareEvaluationEndInput");

  // Read current URL parameters
  const params = new URLSearchParams(window.location.search);

  // Restore previous compare state if URL is empty
  if (!params.has("asset1")) {

    const savedAssetOne = localStorage.getItem("compareAssetOne");
    const savedAssetTwo = localStorage.getItem("compareAssetTwo");
    const savedSource = localStorage.getItem("compareSource");
    const savedTestMode = localStorage.getItem("compareTestMode");
    const savedStart = localStorage.getItem("compareEvaluationStart");
    const savedEnd = localStorage.getItem("compareEvaluationEnd");

    // Redirect using saved values
    if (savedAssetOne && savedAssetTwo) {

      const redirectParams = new URLSearchParams();

      redirectParams.set("asset1", savedAssetOne);
      redirectParams.set("asset2", savedAssetTwo);
      redirectParams.set("source", savedSource || "kaggle");
      redirectParams.set("test_mode", savedTestMode || "original");
      redirectParams.set("evaluation_start", savedStart || "2010-02-02");
      redirectParams.set("evaluation_end", savedEnd || "2010-05-03");

      window.location.replace(
        `/compare-assets?${redirectParams.toString()}`
      );

      return;
    }
  }

  // Save form state on submit
  form.addEventListener("submit", () => {

    // Save first asset
    if (assetOneInput) {

      const assetOne = (
        assetOneInput.value
        .trim()
        .toUpperCase()
      );

      assetOneInput.value = assetOne;

      localStorage.setItem("compareAssetOne", assetOne);
    }

    // Save second asset
    if (assetTwoInput) {

      const assetTwo = (
        assetTwoInput.value
        .trim()
        .toUpperCase()
      );

      assetTwoInput.value = assetTwo;

      localStorage.setItem("compareAssetTwo", assetTwo);
    }

    // Save selected test mode
    if (testModeSelect) {
      localStorage.setItem(
        "compareTestMode",
        testModeSelect.value
      );
    }

    // Save evaluation start date
    if (evaluationStartInput) {
      localStorage.setItem(
        "compareEvaluationStart",
        evaluationStartInput.value
      );
    }

    // Save evaluation end date
    if (evaluationEndInput) {
      localStorage.setItem(
        "compareEvaluationEnd",
        evaluationEndInput.value
      );
    }

    // Save selected source
    if (sourceSelect) {
      localStorage.setItem(
        "compareSource",
        sourceSelect.value
      );
    }
  });
}


// Initialize compare state after page load
document.addEventListener("DOMContentLoaded", () => {

  setupCompareAssetsState();

});