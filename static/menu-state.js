// Get the most recently analysed or selected asset
function getLastAnalysedAsset() {
  return (
    localStorage.getItem("lastAnalysedAsset") ||
    localStorage.getItem("loadedAsset") ||
    localStorage.getItem("selectedAsset") ||
    "AAPL"
  ).trim().toUpperCase();
}


// Update global menu links using the saved asset state
function updateGlobalMenuLinks() {
  const asset = getLastAnalysedAsset();

  const menuPredictionLink = document.getElementById("menuPredictionLink");
  const menuDashboardLink = document.getElementById("menuDashboardLink");

  // Point prediction link to latest asset
  if (menuPredictionLink) {
    menuPredictionLink.href = `/predictions/${asset}`;
  }

  // Point dashboard link to latest asset and saved test settings
  if (menuDashboardLink) {
    const testMode = localStorage.getItem("testMode") || "original";
    const evaluationStart = localStorage.getItem("evaluationStart") || "2010-02-02";
    const evaluationEnd = localStorage.getItem("evaluationEnd") || "2010-05-03";

    const params = new URLSearchParams();

    params.set("asset", asset);
    params.set("test_mode", testMode);
    params.set("evaluation_start", evaluationStart);
    params.set("evaluation_end", evaluationEnd);

    menuDashboardLink.href = `/dashboard?${params.toString()}`;
  }
}


// Apply menu link updates after page load
document.addEventListener("DOMContentLoaded", () => {
  updateGlobalMenuLinks();
});