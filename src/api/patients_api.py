from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends, Response
from sqlmodel import Session, select
import pandas as pd
from io import BytesIO
from auth.auth_service import AuthService
from db.manager import Database
from schema.schema import Patients, PatientsCreate, PatientsPublic, PatientsPublicWithWounds, PatientsUpdate, TrackingRecords, Wounds, WoundsPublic
from schema.schema import Comorbidities, ComorbiditiesCreate, ComorbiditiesPublic, PatientComorbidities

patients_router = APIRouter(
    dependencies=[Depends(AuthService.get_current_user)]
)
BASE_URL_PATIENTS = "/patients/"


@patients_router.post(BASE_URL_PATIENTS, response_model=PatientsPublic)
def create_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient: PatientsCreate
):
    """Create a new patient"""
    now = datetime.now()
    patient_for_database = Patients(name = patient.name, gender = patient.gender, birthday = patient.birthday, email = patient.email, hospital_registration = patient.hospital_registration, phone_number = patient.phone_number, height = patient.height, weight = patient.weight, smoke_frequency = patient.smoke_frequency, drink_frequency = patient.drink_frequency, accept_tcle = patient.accept_tcle, specialist_id = patient.specialist_id, created_at=now, updated_at=now)
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


@patients_router.patch(BASE_URL_PATIENTS + "{patient_id}", response_model=PatientsPublic)
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


@patients_router.get(BASE_URL_PATIENTS + "{patient_id}", response_model=PatientsPublic)
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


@patients_router.get(BASE_URL_PATIENTS, response_model=list[PatientsPublic])
def get_all_patients(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all patients"""
    patients = session.exec(select(Patients).offset(offset).limit(limit)).all()
    return patients

@patients_router.get(BASE_URL_PATIENTS + "{patient_id}" + "/wounds", response_model=PatientsPublicWithWounds)
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

@patients_router.get(BASE_URL_PATIENTS + "{patient_id}" + "/wounds/excel", response_model=WoundsPublic)
def export_to_excel(
    *,
    session: Session = Depends(Database.get_session),
    patient_id: int
):
    """ Export all wounds to excel """
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    wounds = session.exec(select(Wounds).where(Wounds.patient_id == patient.patient_id)).all()
    if not wounds:
        raise HTTPException(status_code=404, detail="No wounds found for this patient")

    tracking_records = session.exec(select(TrackingRecords).where(TrackingRecords.wound_id.in_([w.wound_id for w in wounds]))).all()

    wounds_data = [{
        "ID": wound.wound_id,
        "Região": wound.wound_region,
        "Subregião": wound.wound_subregion,
        "Tipo": wound.wound_type,
        "Data de começo": wound.start_date,
        "Data de final": wound.end_date,
        "Criado em": wound.created_at,
        "Atualizado em": wound.updated_at
    } for wound in wounds]

    wounds_df = pd.DataFrame(wounds_data)

    updates_data = [{
        "ID da ferida": tracking_record.wound_id,
        "Tamanho": tracking_record.wound_size,
        "Quantidade de exsudato": tracking_record.exudate_amount,
        "Tipo de exsudato": tracking_record.exudate_type,
        "Tipo de tecido": tracking_record.tissue_type,
        "Bordas da ferida": tracking_record.wound_edges,
        "Pele ao redor da ferida": tracking_record.skin_around_the_wound,
        "Teve febre": "Sim" if tracking_record.had_a_fever else "Não",
        "Nível de dor": tracking_record.pain_level,
        "Quantidade de trocas de curativo no dia": tracking_record.dressing_changes_per_day,
        "Orientações dadas ao paciente": tracking_record.guidelines_to_patient,
        "Anotações extras": tracking_record.extra_notes,
        "Criado em": tracking_record.created_at,
        "Atualizado em": tracking_record.updated_at,
    } for tracking_record in tracking_records]

    updates_df = pd.DataFrame(updates_data)

    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            wounds_df.to_excel(writer, index=False, sheet_name="Feridas")
            updates_df.to_excel(writer, index=False, sheet_name="Atualizações das feridas")
        buffer.seek(0)
        excel_data = buffer.read()
    
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=feridas_paciente_{patient_id}.xlsx"
        }
    )