from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from auth.auth_service import AuthService
from db.manager import Database
from schema.schema import Specialists
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
import requests as rq
from google_auth_oauthlib.flow import Flow
import os
import json

login_router = APIRouter()

# Add this line to disable HTTPS checking during development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This variable specifies the name of a file that contains the OAuth 2.0 information for this application
# CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")

# print('===== CLIENT_SECRETS_FILE =====')
# print(CLIENT_SECRETS_FILE)
# with open(CLIENT_SECRETS_FILE, 'r') as file:
#     client_secrets = file.read()
#     print('===== CLIENT SECRETS CONTENT =====')
#     print(client_secrets)

# These OAuth 2.0 scopes allow access to the user's Google account OpenID, Email, and Profile.
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

client_secrets = {
    "web":{
        "client_id":os.getenv('CLIENT_ID'),
        "project_id":"wounds",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":os.getenv('CLIENT_SECRET'),
        "redirect_uris":[os.getenv('SERVER_URL')]
    }
}

@login_router.get('/auth/login/google')
async def call_google_signin(request: Request):
    # flow = Flow.from_client_secrets_file(
    #     CLIENT_SECRETS_FILE, 
    #     scopes=SCOPES
    # )
    # client_secrets_content = os.getenv('CLIENT_SECRETS_CONTENT')
    # if not client_secrets_content:
    #     raise HTTPException(status_code=500, detail="Client secrets not found in environment variables")

    # client_secrets = json.loads(client_secrets_content)

    flow = Flow.from_client_config(
        client_secrets, 
        scopes=SCOPES
    )
    flow.redirect_uri = 'http://localhost:8000/auth/login/google/callback'
    auth_url, state = flow.authorization_url(
        access_type='offline'
    )
    request.session['state'] = state
    return RedirectResponse(auth_url)

@login_router.get('/auth/login/google/callback')
async def callback_uri(request: Request, session: Session = Depends(Database.get_session)):
    state = request.session.get('state')
    # flow = Flow.from_client_secrets_file(
    #     CLIENT_SECRETS_FILE, 
    #     scopes=SCOPES, 
    #     state=state
    # )
    flow = Flow.from_client_config(
        client_secrets, 
        scopes=SCOPES
    )
    flow.redirect_uri = 'http://localhost:8000/auth/login/google/callback'

    authorization_response = str(request.url)

    print('===== autorization_response =====')
    print(authorization_response)

    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    user_info=None
    try:
        info = rq.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={flow.credentials.token}")
        user_info = info.json()
    except ValueError:
        raise HTTPException(status_code=401, detail="token inválido")

    statement = select(Specialists).where(Specialists.email == user_info['email'])
    specialist = session.exec(statement).first()
    if specialist is None:
        specialist = Specialists(email=user_info['email'], name=user_info["name"])
        session.add(specialist)
        session.commit()
        session.refresh(specialist)

    # adds the information we need from the user to the cookies
    request.session['id'] = specialist.specialist_id
    request.session['email'] = user_info['email']
    required_fields = [specialist.birthday, specialist.state, specialist.city, specialist.speciality]
    if all(field is None for field in required_fields):
        return RedirectResponse(os.getenv("CLIENT_REDIRECT", 'http://localhost:5173))
    else:
        return RedirectResponse(os.getenv("CLIENT_REDIRECT", 'http://localhost:5173'))

# endpoint 'protegido' para buscar o usario ativo atualmente usando o token dos cookies
@login_router.get("/specialists/me")
async def me(request: Request, current_user = Depends(AuthService.get_current_user)):
    return request.session

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
