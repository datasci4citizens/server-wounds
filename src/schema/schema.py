from datetime import datetime, date
from sqlmodel import Field, SQLModel, Relationship

""" SPECIALISTS TABLES """
class SpecialistsBase(SQLModel):
    email: str
    name: str
    is_allowed: bool

class SpecialistsCreate(SpecialistsBase):
    pass

class SpecialistsPublic(SpecialistsBase):
    specialist_id: int
    created_at: datetime
    updated_at: datetime

class SpecialistsUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    is_allowed: bool | None = None

class Specialists(SpecialistsBase, table=True):
    specialist_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime

    patients: list["Patients"] = Relationship(back_populates="specialist")
    tracking_records: list["TrackingRecords"] = Relationship(back_populates="specialist")

""" COMORBIDITIES TABLES """
class ComorbiditiesBase(SQLModel):
    cid11_code: str
    name: str

class ComorbiditiesCreate(ComorbiditiesBase):
    pass

class ComorbiditiesPublic(ComorbiditiesBase):
    comorbidity_id: int

class ComorbiditiesUpdate(SQLModel):
    cid11_code: str | None = None
    name: str | None = None

class Comorbidities(ComorbiditiesBase, table=True):
    comorbidity_id: int = Field(default=None, primary_key=True) # ta dando erro

    patients: list["PatientComorbidities"] = Relationship(back_populates="comorbidity")

class PatientComorbidities(SQLModel, table=True):
    patient_id: int = Field(foreign_key="patients.patient_id", primary_key=True)
    comorbidity_id: int = Field(foreign_key="comorbidities.comorbidity_id", primary_key=True)

    # Relacionamentos para paciente e comorbidade
    patient: "Patients" = Relationship(back_populates="comorbidities")
    comorbidity: Comorbidities = Relationship(back_populates="patients")

""" PATIENTS TABLES """
class PatientsBase(SQLModel):
    name: str
    gender: str
    birthday: date
    email: str
    phone_number: str
    accept_tcle: bool
    specialist_id: int = Field(foreign_key="specialists.specialist_id")

class PatientsCreate(PatientsBase):
    pass

class PatientsUpdate(SQLModel):
    name: str | None = None
    gender: str | None = None
    birthday: date | None = None
    email: str | None = None
    phone_number: str | None = None
    accept_tcle: bool | None = None

class PatientsPublic(PatientsBase):
    patient_id: int
    created_at: datetime
    updated_at: datetime

class Patients(PatientsBase, table=True):
    patient_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    
    specialist: "Specialists" = Relationship(back_populates="patients") # não sei se ta certo
    comorbidities: list[PatientComorbidities] = Relationship(back_populates="patient")
    wounds: list["Wounds"] = Relationship(back_populates="patient")
    # tracking_records: list["TrackingRecords"] = Relationship(back_populates="patient")

""" WOUNDS TABLES """
""" no tutorial do sqlmodel, wounds é o hero e patient e wound_type é o team"""
class WoundsBase(SQLModel):
    wound_location: str 
    wound_type: str
    start_date: date
    end_date: date | None = None
    patient_id: int = Field(foreign_key="patients.patient_id")

class WoundsCreate(WoundsBase):
    pass

class WoundsUpdate(SQLModel):
    # wound_location: str | None = None # acho que não deveria da pra mudar a localização da ferida
    # start_date: datetime | None = None
    end_date: date | None = None
    # wound_type_id: int | None = None

class WoundsPublic(WoundsBase):
    wound_id: int

class Wounds(WoundsBase, table = True):
    wound_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    patient: "Patients" = Relationship(back_populates="wounds")

    tracking_records: list["TrackingRecords"] = Relationship(back_populates="wound")

""" TRACKING RECORDS TABLES"""
class TrackingRecordsBase(SQLModel):
    wound_size: str
    wound_size_score: int
    exudate_amount: str
    exudate_type: str
    tissue_type: str 
    wound_edges: str | None = None
    skin_around_the_wound: str | None = None
    had_a_fever: bool | None = None
    pain_level: str | None = None
    dressing_changes_per_day: str | None = None
    conduct: str | None = None
    extra_notes: str | None = None
    image_id: int
    # patient_id: int = Field(foreign_key="patients.patient_id")
    wound_id: int = Field(foreign_key="wounds.wound_id")
    specialist_id: int = Field(foreign_key="specialists.specialist_id")

class TrackingRecordsCreate(TrackingRecordsBase):
    pass

class TrackingRecordsUpdate(SQLModel):
    wound_size: float | None = None 
    wound_size_score: int | None = None
    exudate_amount: str | None = None
    exudate_amount_score: int | None = None
    exudate_type: str | None = None
    tissue_type: str | None = None
    tissue_type_score: int | None = None
    wound_edges: str | None = None 
    skin_around_the_wound: str | None = None 
    had_a_fever: bool | None = None
    pain_level: str | None = None
    dressing_changes_per_day: str | None = None
    conduct: str | None = None
    extra_notes: str | None = None
    image_id: int | None = None

class TrackingRecordsPublic(TrackingRecordsBase):
    tracking_record_id: int
    created_at: datetime
    updated_at: datetime

class TrackingRecords(TrackingRecordsBase, table = True):
    tracking_record_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    # patient: Patients = Relationship(back_populates="tracking_records")
    wound: Wounds = Relationship(back_populates="tracking_records")
    specialist: Specialists = Relationship(back_populates="tracking_records")

""" DATA MODELS FOR RELATIONSHIPS """
class PatientsPublicWithWounds(PatientsPublic):
    wounds: list[WoundsPublic] = []

class WoundsPublicWithPatient(WoundsPublic):
    patient: PatientsPublic | None = None

class WoundsPublicWithTrackingRecords(WoundsPublic):
    tracking_records: list[TrackingRecordsPublic] = []

class SpecialistsPublicWithTrackingRecords(SpecialistsPublic):
    pass
