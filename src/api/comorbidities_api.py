from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from db.manager import Database
from schema.schema import Comorbidities, ComorbiditiesCreate, ComorbiditiesPublic, ComorbiditiesUpdate

comorbidities_router = APIRouter()
BASE_URL_COMORBIDITIES = "/comorbidities/"

# The creation of comorbidities will happen when creating patients, so there will not be an exclusive endpoint for this, for now
@comorbidities_router.patch(BASE_URL_COMORBIDITIES + "{comorbidity_id}", response_model=ComorbiditiesPublic)
def update_comorbidity(
        *,
        session: Session = Depends(Database.get_session),
        comorbidity_id: int,
        comorbidity: ComorbiditiesUpdate
):
    """Update comorbidity"""
    # https://id.who.int/swagger/index.html -> api's endpoints (swagger)
    # https://icd.who.int/docs/icd-api/APIDoc-Version2/ -> api's documentation
    db_comorbidity = session.get(Comorbidities, comorbidity_id)
    if not db_comorbidity:
        raise HTTPException(status_code=404, detail="Comorbidity not found")
    comorbidity_data = comorbidity.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_comorbidity.sqlmodel_update(comorbidity_data, update=updated_at)
    session.add(db_comorbidity)
    session.commit()
    session.refresh(db_comorbidity)
    return db_comorbidity


@comorbidities_router.get(BASE_URL_COMORBIDITIES + "{comorbidity_id}", response_model=ComorbiditiesPublic)
def get_comorbidity_by_id(
        *,
        session: Session = Depends(Database.get_session),
        comorbidity_id: int
):
    """Get specific comorbidity"""
    comorbidity = session.get(Comorbidities, comorbidity_id)
    if not comorbidity:
        raise HTTPException(status_code=404, detail="Comorbidity not found")
    return comorbidity

@comorbidities_router.get(BASE_URL_COMORBIDITIES, response_model=list[ComorbiditiesPublic])
def get_all_comorbidities(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all comorbidities"""
    types = session.exec(select(Comorbidities).offset(offset).limit(limit)).all()
    return types


@comorbidities_router.delete(BASE_URL_COMORBIDITIES + "{comorbidity_id}")
def delete_comorbidity(
        *,
        session: Session = Depends(Database.get_session),
        comorbidity_id: int
):
    """Delete comorbidity"""
    comorbidity = session.get(Comorbidities, comorbidity_id)
    if not comorbidity:
        raise HTTPException(status_code=404, detail="Comorbidity not found")
    session.delete(comorbidity)
    session.commit()
    return {"ok": True}