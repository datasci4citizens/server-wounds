from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from auth.auth_service import AuthService
from schema.schema import TrackingRecords, Wounds
from schema.schema import WoundsPublic
from schema.schema import WoundsCreate
from schema.schema import WoundsUpdate
from schema.schema import WoundsPublicWithTrackingRecords
from db.manager import Database

wounds_router = APIRouter(
    dependencies=[Depends(AuthService.get_current_user)]
)
BASE_URL_WOUNDS = "/wounds/"

@wounds_router.post(BASE_URL_WOUNDS, response_model=WoundsPublic)
def create_wound(
        *,
        session: Session = Depends(Database.get_session),
        wound: WoundsCreate
):
    """Create a new wound"""
    dates = {"is_active": True, "created_at": datetime.now(), "updated_at": datetime.now()}
    if wound.start_date == None:
        dates.update({"start_date": datetime.now})
    db_wound = Wounds.model_validate(wound, update=dates)
    session.add(db_wound)
    session.commit()
    session.refresh(db_wound)
    return db_wound

@wounds_router.patch(BASE_URL_WOUNDS + "{wound_id}", response_model=WoundsPublic)
def update_wound(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int,
        wound: WoundsUpdate
):
    """Update wound end date"""
    db_wound = session.get(Wounds, wound_id)
    if not db_wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    wound_data = wound.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_wound.sqlmodel_update(wound_data, update=updated_at)
    session.add(db_wound)
    session.commit()
    session.refresh(db_wound)
    return db_wound

@wounds_router.get(BASE_URL_WOUNDS + "{wound_id}", response_model=WoundsPublic)
def get_wound_by_id(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int
):
    """Get specific wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    return wound

@wounds_router.get(BASE_URL_WOUNDS + "{wound_id}" + "/tracking-records", response_model=WoundsPublicWithTrackingRecords)
def get_wound_tracking_records(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100),
        wound_id: int
):
    """Get all tracking records from wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    return wound

@wounds_router.put(BASE_URL_WOUNDS + "{wound_id}" + "/archive", response_model=WoundsPublic)
def archive_wound(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int
):
    """Archive wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    
    tracking_records = session.exec(select(TrackingRecords).where(TrackingRecords.wound_id == wound_id)).all()
    if not tracking_records:
        raise HTTPException(status_code=404, detail="Tracking records for the wound not found")
    
    for tracking_record in tracking_records:
        tracking_record.is_active = False
        tracking_record.updated_at = datetime.now()
        session.add(tracking_record)
        session.commit()
        session.refresh(tracking_record)

    wound.is_active = False
    session.add(wound)
    session.commit()
    session.refresh(wound)
    return wound