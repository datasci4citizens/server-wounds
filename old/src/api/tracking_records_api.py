from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session
from auth.auth_service import AuthService
from db.manager import Database
from schema.schema import TrackingRecords, TrackingRecordsCreate, TrackingRecordsPublic, TrackingRecordsUpdate

tracking_records_router = APIRouter(
    dependencies=[Depends(AuthService.get_current_user)],
    tags = ["tracking_records"]
)
BASE_URL_TRACKING_RECORDS = "/tracking-records/"

@tracking_records_router.post(BASE_URL_TRACKING_RECORDS, response_model=TrackingRecordsPublic)
def create_tracking_record(
        *,
        request: Request,
        session: Session = Depends(Database.get_session),
        tracking_record: TrackingRecordsCreate
):
    """Create a new tracking record"""
    update_fields = {
        "is_active": True,
        "specialist_id": request.session.get("id"),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    db_tracking_record = TrackingRecords.model_validate(tracking_record, update=update_fields)
    session.add(db_tracking_record)
    session.commit()
    session.refresh(db_tracking_record)
    return db_tracking_record

@tracking_records_router.patch(BASE_URL_TRACKING_RECORDS +
                               "{tracking_record_id}", response_model=TrackingRecordsPublic)
def update_tracking_record(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record_id: int,
        tracking_record: TrackingRecordsUpdate
):
    """Update tracking record"""
    db_tracking_record = session.get(TrackingRecords, tracking_record_id)
    if not db_tracking_record:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    tracking_record_data = db_tracking_record.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_tracking_record.sqlmodel_update(tracking_record_data, update=updated_at)
    session.add(db_tracking_record)
    session.commit()
    session.refresh(db_tracking_record)
    return db_tracking_record

@tracking_records_router.get(BASE_URL_TRACKING_RECORDS +
                             "{tracking_record_id}", response_model=TrackingRecordsPublic)
def get_tracking_record_by_id(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record_id: int
):
    """Get specific tracking record"""
    tracking_record = session.get(TrackingRecords, tracking_record_id)
    if not tracking_record:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    return tracking_record

@tracking_records_router.put(BASE_URL_TRACKING_RECORDS + "{tracking_record_id}" + "/archive", response_model=TrackingRecordsPublic)
def archive_tracking_record(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record_id: int
):
    """Archive tracking record"""
    db_tracking_record = session.get(TrackingRecords, tracking_record_id)
    if not db_tracking_record:
        raise HTTPException(status_code=404, detail="Tracking record not found")

    tracking_record_data = db_tracking_record.model_dump(exclude_unset=True)
    archive = {"is_active": False, "updated_at": datetime.now()}
    db_tracking_record.sqlmodel_update(tracking_record_data, update=archive)
    session.add(db_tracking_record)
    session.commit()
    session.refresh(db_tracking_record)
    return db_tracking_record
