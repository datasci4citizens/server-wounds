from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from db.manager import Database
from api.users_api import router
from api.specialist_api import specialist_router
from api.patients_api import patients_router
from api.wounds_api import wounds_router
from api.tracking_records_api import tracking_records_router
from api.comorbidities_api import comorbidities_router

Database.db_engine()

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000"
]

# <TODO: Change the allow_origins to the actual domain>
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(specialist_router)
app.include_router(patients_router)
app.include_router(wounds_router)
app.include_router(tracking_records_router)
app.include_router(comorbidities_router)
