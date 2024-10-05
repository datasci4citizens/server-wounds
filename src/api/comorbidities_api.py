from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from db.manager import Database
from schema.schema import Comorbidities, ComorbiditiesCreate, ComorbiditiesPublic, ComorbiditiesUpdate

comorbidities_router = APIRouter()
BASE_URL_WOUNDS_TYPE = "/comorbidities/"

@comorbidities_router.post(BASE_URL_WOUNDS_TYPE, response_model=ComorbiditiesPublic)
def create_comorbidity(
        *,
        session: Session = Depends(Database.get_session),
        comorbidity: ComorbiditiesCreate
):
    """Create a new comorbidity"""
    # na criação de uma nova comorbidade, devemos adicionar um busca a api do cid11 para verificar se realmente existe a doença
    # https://id.who.int/swagger/index.html -> endpoints da api (swagger)
    # https://icd.who.int/docs/icd-api/APIDoc-Version2/ -> documentação da api
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_comorbidity = Comorbidities.model_validate(comorbidity, update=dates)
    session.add(db_comorbidity)
    session.commit()
    session.refresh(db_comorbidity)
    return db_comorbidity


@comorbidities_router.patch(BASE_URL_WOUNDS_TYPE + "{comorbidity_id}", response_model=ComorbiditiesPublic)
def update_comorbidity(
        *,
        session: Session = Depends(Database.get_session),
        comorbidity_id: int,
        comorbidity: ComorbiditiesUpdate
):
    """Update comorbidity"""
    # na atualização de uma nova comorbidade, devemos adicionar um busca a api do cid11 para verificar se realmente existe a doença
    # https://id.who.int/swagger/index.html -> endpoints da api (swagger)
    # https://icd.who.int/docs/icd-api/APIDoc-Version2/ -> documentação da api
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


@comorbidities_router.get(BASE_URL_WOUNDS_TYPE + "{comorbidity_id}", response_model=ComorbiditiesPublic)
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


@comorbidities_router.get(BASE_URL_WOUNDS_TYPE, response_model=list[ComorbiditiesPublic])
def get_all_comorbidities(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all comorbidities"""
    types = session.exec(select(Comorbidities).offset(offset).limit(limit)).all()
    return types


@comorbidities_router.delete(BASE_URL_WOUNDS_TYPE + "{comorbidity_id}")
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