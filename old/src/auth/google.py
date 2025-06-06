from typing import Any, Dict
import os
from fastapi import HTTPException, status
import requests

GOOGLE_ID_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://accounts.google.com/o/oauth2/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


# Exchange authorization token with access token
# https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
def google_get_access_token(code: str, redirect_uri: str) -> str:
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        raise HTTPException(status_code=403, detail=f"Could not get access token from Google: {response.json()}")

    access_token = response.json()["access_token"]

    return access_token


# Get user info from google
# https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
def google_get_user_info(access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={"access_token": access_token},
    )

    if not response.ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not get user info from Google: {response.json()}",
            headers={"WWW-Authenticate": "Bearer"},
)
    return response.json()


def google_get_user_data(validated_data):
    # https://github.com/MomenSherif/react-oauth/issues/252
    redirect_uri = "postmessage"

    code = validated_data.code
    
    access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)

    return google_get_user_info(access_token=access_token)