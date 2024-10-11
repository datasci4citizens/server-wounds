from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from db.manager import Database
from schema.schema import Patients, PatientsCreate, PatientsPublic, PatientsPublicWithWounds, PatientsUpdate
from schema.schema import Comorbidities, ComorbiditiesCreate, ComorbiditiesPublic, PatientComorbidities

wounds_patients_router = APIRouter()
BASE_URL_PATIENTS = "/patients/"


@wounds_patients_router.post(BASE_URL_PATIENTS, response_model=PatientsPublic)
def create_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient: PatientsCreate
):
    """Create a new patient"""
    now = datetime.now()
    patient_for_database = Patients(name = patient.name, gender = patient.gender, birthday = patient.birthday, email = patient.email, phone_number = patient.phone_number, accept_tcle = patient.accept_tcle, specialist_id = patient.specialist_id, created_at=now, updated_at=now)
    # db_patient = Patients.model_validate(patient_for_database, update=dates)
    session.add(patient_for_database)
    session.commit()
    session.refresh(patient_for_database)

    patients_comorbidities_ids = []

    if patient.comorbidities_to_add != None:
        for comorbidity in patient.comorbidities_to_add:
            statement = select(Comorbidities).where(Comorbidities.name == comorbidity)
            db_comorbidity = session.exec(statement).first()

            if not db_comorbidity:
                new_comorbidity = Comorbidities(name=comorbidity) # in the future, use the cid11 api
                session.add(new_comorbidity)
                session.commit()
                session.refresh(new_comorbidity)
                patients_comorbidities_ids.append(new_comorbidity.comorbidity_id)
            else:
                patients_comorbidities_ids.append(db_comorbidity.comorbidity_id)

    patient.comorbidities.extend(patients_comorbidities_ids)

    for comorbidity_id in patient.comorbidities:
        patient_comorbidity = PatientComorbidities(patient_id=patient_for_database.patient_id, comorbidity_id=comorbidity_id)
        session.add(patient_comorbidity)
        session.commit()
        session.refresh(patient_comorbidity)
    return patient_for_database


@wounds_patients_router.patch(BASE_URL_PATIENTS + "{patient_id}", response_model=PatientsPublic)
def update_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int,
        patient: PatientsUpdate
):
    """Update patient"""
    db_patient = session.get(Patients, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_data = patient.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_patient.sqlmodel_update(patient_data, update=updated_at)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)

    patients_comorbidities = []

    if patient.comorbidities_to_add != None:
        for comorbidity in patient.comorbidities_to_add:
            statement = select(Comorbidities).where(Comorbidities.name == comorbidity.name)
            db_comorbidity = session.exec(statement).first()

            if not db_comorbidity:
                new_comorbidity = ComorbiditiesCreate(name=comorbidity) # in the future, use the cid11 api
                session.add(new_comorbidity)
                session.commit()
                session.refresh(new_comorbidity)
                patients_comorbidities.append(new_comorbidity)
            else:
                patients_comorbidities.append(db_comorbidity)
    
    patients_comorbidities.append(patient.comorbidities)

    for comorbidity in patients_comorbidities:
        statement = select(PatientComorbidities).where(PatientComorbidities.patient_id == db_patient.patient_id and PatientComorbidities.comorbidity_id == comorbidity.comorbidity_id)
        db_patient_comorbidity = session.exec(statement).first()
        if not db_patient_comorbidity:
            patient_comorbidity = PatientComorbidities(patient_id=db_patient.patient_id, comorbidity_id=comorbidity.comorbidity_id)
            session.add(patient_comorbidity)
            session.commit()
            session.refresh(patient_comorbidity)

    return db_patient


@wounds_patients_router.get(BASE_URL_PATIENTS + "{patient_id}", response_model=PatientsPublic)
def get_patient_by_id(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int
):
    """Get specific patient"""
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@wounds_patients_router.get(BASE_URL_PATIENTS, response_model=list[PatientsPublic])
def get_all_patients(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all patients"""
    patients = session.exec(select(Patients).offset(offset).limit(limit)).all()
    return patients

@wounds_patients_router.get(BASE_URL_PATIENTS + "{patient_id}" + "/wounds", response_model=PatientsPublicWithWounds)
def get_patient_wounds(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int
):
    """ Get patient with wounds """
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# ao remover um paciente, eu tenho que remover todas as feridas relacionadas
@wounds_patients_router.delete(BASE_URL_PATIENTS + "{patient_id}")
def delete_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int
):
    """Delete patient"""
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(patient)
    session.commit()
    return {"ok": True}