from fastapi import Request
from fastapi.templating import Jinja2Templates

from helpers.finance_helpers import getModelResults

# model results page
async def modelResultsView(request: Request, templates: Jinja2Templates):
    model_results = getModelResults()

    return templates.TemplateResponse(request=request, name="model_results.html", context={"models_results": model_results, "isAuthorized": False})

