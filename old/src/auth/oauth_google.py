from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from auth.auth_service import AuthService, AuthUser
from auth.google import google_get_user_data
from db.manager import Database
from schema.schema import Specialists
from sqlmodel import Session, select
import requests as rq
from google_auth_oauthlib.flow import Flow
import os
from typing import Annotated

login_router = APIRouter()

class AuthCode(BaseModel):
    code: str

class Token(BaseModel):
    access: str
    token_type: str

@login_router.post('/auth/login/google')
async def google_login(code: AuthCode, request: Request, session: Session = Depends(Database.get_session)):  
    # get user data from google
    user_data = google_get_user_data(code)

    # Creates user in DB if first time login
    
    user_email = user_data.get("email")
    user_username = user_data.get("given_name")
 
    statement = select(Specialists).where(Specialists.email == user_email)
    specialist = session.exec(statement).first()
    if specialist is None:
        specialist = Specialists(email=user_email, name=user_username)
        session.add(specialist)
        session.commit()
        session.refresh(specialist)
    access_token = AuthService.create_access_token(user_email)
    return Token(access=access_token, token_type="bearer")


# endpoint 'protegido' para buscar o usario ativo atualmente usando o token dos cookies
@login_router.get("/auth/me")
async def me(request: Request, current_user : Annotated[AuthUser, Depends(AuthService.get_current_user)]):
    return current_user

