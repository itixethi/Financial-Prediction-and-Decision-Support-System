from urllib import request
from fastapi import Form
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token 
from google.auth.transport import requests

from controllers.dashboard import dashboardView
from controllers.model_results import modelResultsView
from controllers.correlations import correlationsView
from controllers.predictions import predictionsView
from controllers.assets import assetsView, assetDetailView
from controllers.login import loginView
from controllers.compare_models import compareModelsView
from firebase.helpers import validateFirebaseToken

from helpers.finance_helpers import getModelResults, getCorrelations, getPredictionsByAsset

# calling app for routing 
app = FastAPI()

# firebase adapter used to validate brower login token
firebase_request_adapter = requests.Request()


# define static and template folders
app.mount ("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        id_token = request.cookies.get("token")
        user_token = validateFirebaseToken(id_token=id_token, firebase_request_adapter=firebase_request_adapter)
        isAuthorized = user_token is not None
        return templates.TemplateResponse(request=request, name="index.html", context={"isAuthorized": isAuthorized})
    except Exception as e:
        return HTMLResponse(str(e), status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
     return await loginView(request=request, templates=templates)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return await dashboardView(request=request, templates=templates)

@app.get("/assets", response_class=HTMLResponse)
async def assets(request: Request):
    return await assetsView(request=request, templates=templates)

@app.get("/assets/{symbol}", response_class=HTMLResponse)
async def asset_detail(request: Request, symbol: str):
    return await assetDetailView(request=request, templates=templates, symbol=symbol)

@app.get("/model-results", response_class=HTMLResponse)
async def modelResults(request: Request):
    return await modelResultsView(request=request, templates=templates)

@app.get("/correlations", response_class=HTMLResponse)
async def correlations(request: Request):
    return await correlationsView(request=request, templates=templates)

@app.get("/predictions/{asset}", response_class=HTMLResponse)
async def predictions(request: Request, asset: str):
    return await predictionsView(request=request, templates=templates, asset=asset)

@app.get("/compare-models", response_class=HTMLResponse)
async def compareModels(request: Request):
    return await compareModelsView(request=request, templates=templates)

@app.get("/api/model-results")
async def apiModelResults():
    return JSONResponse(content=getModelResults())

@app.get("/api/correlations")
async def apiCorrelations():
    return JSONResponse(content=getCorrelations())

@app.get("/api/predictions/{asset}")
async def apiPredictions(asset: str):
    return JSONResponse(content=getPredictionsByAsset(asset))

@app.post("/api/run-analysis/{asset}")
async def apiRunAnalysis(asset: str):
    return {
        "asset": asset.upper(),
        "status": "success",
        "message": f"Analysis for {asset.upper()}. In the next phase this runs Python model pipeline.",
        "current_stage": "Prototype simulation"
    }

