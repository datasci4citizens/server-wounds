"""
This module provides utility functions for authenticating users with Google OAuth2.

It supports web-based authentication using the auth-code from @react-oauth/google:
- Exchanges an authorization code for an access token to retrieve user data.

It integrates with Django settings for Google API client credentials and manages
error reporting via Django REST Framework's `APIException`.
"""

from typing import Any, Dict

import requests
from django.conf import settings
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger("app_cicatrizando")

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def google_get_access_token(code: str, redirect_uri: str = "postmessage") -> str:
    """
    Exchanges the authorization code for an access token.
    
    @react-oauth/google uses 'postmessage' as redirect_uri when the code
    is obtained via popup or implicit flow.
    
    Ref: https://github.com/MomenSherif/react-oauth/issues/252
    """
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    
    if not response.ok:
        error_detail = response.json()
        logger.error(f"Google token exchange failed: {error_detail}")
        raise APIException(f"Could not get access token from Google: {error_detail}")

    return response.json()["access_token"]


def google_get_user_info(access_token: str) -> Dict[str, Any]:
    """
    Retrieves user information using the access token.
    
    Ref: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
    """
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={"access_token": access_token},
    )

    if not response.ok:
        error_detail = response.json()
        logger.error(f"Google user info failed: {error_detail}")
        raise APIException(f"Could not get user info from Google: {error_detail}")

    return response.json()


def google_get_user_data(auth_code: str, redirect_uri: str = "postmessage") -> Dict[str, Any]:
    """
    Main function to authenticate user via auth-code from @react-oauth/google.
    
    1. Exchanges the auth-code for an access token
    2. Uses the access token to retrieve user information
    3. Returns user data in a standardized format
    
    Args:
        auth_code: The authorization code returned by @react-oauth/google
        redirect_uri: The URI to redirect to
        
    Returns:
        Dict with email, name, given_name, family_name and sub (Google user ID)
    """
    logger.info("Exchanging auth code for access token")
    access_token = google_get_access_token(code=auth_code, redirect_uri=redirect_uri)
    
    logger.info("Getting user info from Google")
    user_info = google_get_user_info(access_token=access_token)
    
    email = user_info.get("email")
    if not email:
        raise APIException("Google account does not have an email address")
    
    return {
        "email": email,
        "name": user_info.get("name", ""),
        "given_name": user_info.get("given_name", ""),
        "family_name": user_info.get("family_name", ""),
        "sub": user_info.get("sub", ""),
    }
