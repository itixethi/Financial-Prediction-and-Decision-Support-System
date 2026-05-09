from fastapi import Request
from fastapi.templating import Jinja2Templates


from helpers.finance_helpers import getModelResults

# Display model comparison page
async def compareModelsView(request: Request, templates: Jinja2Templates):

    # Load all saved model evaluation results
    model_results = getModelResults()

    # Render compare models page
    return templates.TemplateResponse(
        request=request,
        name="compare_models.html",
        context={
            "model_results": model_results,
            "isAuthorized": False
        }
    )