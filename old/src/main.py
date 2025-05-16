SECRET_KEY = "segredo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import os
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from db.manager import Database
from auth.oauth_google import login_router
from api.specialist_api import specialist_router
from api.patients_api import patients_router
from api.wounds_api import wounds_router
from api.tracking_records_api import tracking_records_router
from api.comorbidities_api import comorbidities_router
from api.images_api import images_router
from dotenv import load_dotenv
from scalar_fastapi import get_scalar_api_reference

load_dotenv()
load_dotenv(".env.google")
load_dotenv(".env.minio")

Database.db_engine()

app = FastAPI(docs_url=None)

# Modelo de Token

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from this source
    allow_credentials=True,  # Allows sending cookies, authentication tokens and other types of credentials in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
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
app.include_router(images_router)
