from fastapi.responses import HTMLResponse, JSONResponse
import google.oauth2.id_token

# validate Firebase token
def validateFirebaseToken(id_token, firebase_request_adapter):
    if not id_token:
        return None
    
    try:
        return google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except Exception:
        return None
