from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.finance_helpers import getPredictionsByAsset


async def predictionsView(request: Request, templates: Jinja2Templates, asset: str):
    predictions = getPredictionsByAsset(asset)

    # Keep only the last 5 predictions rows for a cleaner page
    preview_predictions = predictions[-5:] if predictions else []

    return templates.TemplateResponse(request=request, name="predictions.html", context={"asset": asset.upper(), "predictions": preview_predictions, "prediction_count": len(predictions), "isAuthorized": False})