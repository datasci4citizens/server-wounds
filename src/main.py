import os
from fastapi import Depends, FastAPI

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from db.manager import Database
from auth.oauth_google import login_router
from api.specialist_api import specialist_router
from api.patients_api import patients_router
from api.wounds_api import wounds_router
from api.tracking_records_api import tracking_records_router
from api.comorbidities_api import comorbidities_router

Database.db_engine()

app = FastAPI()

# Modelo de Token
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from this source
    allow_credentials=True, # Allows sending cookies, authentication tokens and other types of credentials in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8000"
# ]

app.include_router(login_router)
app.include_router(specialist_router)
app.include_router(patients_router)
app.include_router(wounds_router)
app.include_router(tracking_records_router)
app.include_router(comorbidities_router)
