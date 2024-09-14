from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from db.manager import Database
from api.common.users_api import router
from api.wounds.wounds_specialist_api import wounds_specialist_router
from api.wounds.wounds_patients_api import wounds_patients_router
from api.wounds.wounds_type_api import wounds_type_router
from api.wounds.wounds_api import wounds_router
from api.wounds.wounds_tracking_records_api import wounds_tracking_records_router

# <DEACTIVATED: has errors>
# from api.medications.medication_users import medications_user_router
# from api.mih.mih import mih_user_router

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
app.include_router(wounds_specialist_router)
app.include_router(wounds_patients_router)
app.include_router(wounds_type_router)
app.include_router(wounds_router)
app.include_router(wounds_tracking_records_router)

# <DEACTIVATED: has errors>
# app.include_router(medications_user_router)
# app.include_router(mih_user_router)
