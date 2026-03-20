from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import logging

from django.conf import settings
from rest_framework.exceptions import APIException

import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger("app_cicatrizando")
def _get_firebase_app() -> firebase_admin.App:
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", "")
    if not cred_path:
        raise APIException("FIREBASE_CREDENTIALS_PATH is not configured")

    path = Path(cred_path)
    if not path.exists():
        raise APIException("Firebase credentials file not found")

    project_id = getattr(settings, "FIREBASE_PROJECT_ID", "") or None
    options = {"projectId": project_id} if project_id else None

    credential = credentials.Certificate(str(path))
    logger.info("Initializing Firebase Admin SDK")
    if options:
        return firebase_admin.initialize_app(credential, options=options)
    return firebase_admin.initialize_app(credential)


def firebase_get_user_data(id_token: str) -> Dict[str, Any]:
    try:
        app = _get_firebase_app()
        decoded = auth.verify_id_token(id_token, app=app)
    except Exception as exc:
        raise APIException("Invalid Firebase ID token") from exc

    email = decoded.get("email")
    if not email:
        raise APIException("Firebase token does not contain email")

    return {
        "email": email,
        "name": decoded.get("name", ""),
        "given_name": decoded.get("given_name", ""),
        "family_name": decoded.get("family_name", ""),
        "sub": decoded.get("uid") or decoded.get("sub", ""),
    }
