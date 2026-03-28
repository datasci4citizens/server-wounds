"""
Este modulo fornece funcoes utilitarias para autenticar usuarios com o Google OAuth2.

Ele suporta autenticacao baseada na web usando o auth-code do @react-oauth/google:
- Troca um codigo de autorizacao por um token de acesso para recuperar dados do usuario.

Ele se integra as configuracoes do Django para credenciais do cliente da API do Google e gerencia
relatorios de erros por meio da `APIException` do Django REST Framework.
"""

from typing import Any, Dict

import requests
from django.conf import settings
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger("app_cicatrizando")

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def google_get_access_token(code: str) -> str:
    """
    Troca o authorization code por um access token.
    
    O @react-oauth/google usa 'postmessage' como redirect_uri quando o codigo
    e obtido via popup ou fluxo implicit.
    
    Ref: https://github.com/MomenSherif/react-oauth/issues/252
    """
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": "postmessage",
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
    Obtem informacoes do usuario usando o access token.
    
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


def google_get_user_data(auth_code: str) -> Dict[str, Any]:
    """
    Funcao principal para autenticar usuario via auth-code do @react-oauth/google.
    
    1. Troca o auth-code por um access token
    2. Usa o access token para obter informacoes do usuario
    3. Retorna os dados do usuario em formato padronizado
    
    Args:
        auth_code: O codigo de autorizacao retornado pelo @react-oauth/google
        
    Returns:
        Dict com email, name, given_name, family_name e sub (Google user ID)
    """
    logger.info("Exchanging auth code for access token")
    access_token = google_get_access_token(code=auth_code)
    
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
