from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from db.manager import Database
from schema.schema import Patients, Specialists, SpecialistsCreate, SpecialistsPublic, SpecialistsUpdate, SpecialistsPublicWithTrackingRecords,SpecialistsPublicWithPatients

specialist_router = APIRouter()
BASE_URL_SPECIALISTS = "/specialists/"

@specialist_router.post(BASE_URL_SPECIALISTS, response_model=SpecialistsPublic)
def create_specialist(
        *,
        session: Session = Depends(Database.get_session),
        specialist: SpecialistsCreate
):
    """Create a new specialist"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_specialist = Specialists.model_validate(specialist, update=dates)
    session.add(db_specialist)
    session.commit()
    session.refresh(db_specialist)
    return db_specialist
    

@specialist_router.patch(BASE_URL_SPECIALISTS + "{specialist_id}", response_model=SpecialistsPublic)
def update_specialist(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int,
        specialist: SpecialistsUpdate
):
    """Update specialist"""
    specialist_db = session.get(Specialists, specialist_id)
    if not specialist_db:
        raise HTTPException(status_code=404, detail="Specialist not found")
    specialist_data = specialist.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    specialist_db.sqlmodel_update(specialist_data, update=updated_at)
    session.add(specialist_db)
    session.commit()
    session.refresh(specialist_db)
    return specialist_db


@specialist_router.get(BASE_URL_SPECIALISTS + "{specialist_id}", response_model=SpecialistsPublic)
def get_specialist_by_id(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int
):
    """Get specific specialist"""
    specialist = session.get(Specialists, specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist

@specialist_router.get(BASE_URL_SPECIALISTS + "{specialist_id}" + "/tracking-records", response_model=SpecialistsPublicWithTrackingRecords)
def get_specialist_tracking_wounds(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int
):
    """Get tracking records that have been analyzed by an specialist"""
    specialist = session.get(Specialists, specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist

@specialist_router.get(BASE_URL_SPECIALISTS + "{specialist_id}" + "/patients", response_model=SpecialistsPublicWithPatients)
def get_specialist_patients(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int
):
    """Get specialist1s patients"""
    specialist = session.get(Specialists, specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist

@specialist_router.get(BASE_URL_SPECIALISTS, response_model=list[SpecialistsPublic])
def get_all_specialists(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all specialists"""
    specialists = session.exec(select(Specialists).offset(offset).limit(limit)).all()
    return specialists

@specialist_router.delete(BASE_URL_SPECIALISTS + "{patient_id}")
def delete_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int,
        confirmation: bool
):
    """ Delete everything related to the patient """
    if confirmation:
        patient = session.get(Patients, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        session.delete(patient)
        session.commit()
        return {"ok": True}