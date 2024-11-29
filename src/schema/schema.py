from datetime import datetime, date
from sqlmodel import Field, SQLModel, Relationship

""" SPECIALISTS TABLES """
class SpecialistsBase(SQLModel):
    email: str
    name: str
    birthday: date | None = None
    state: str | None = None
    city: str | None = None
    speciality: str | None = None

class SpecialistsCreate(SpecialistsBase):
    pass

class SpecialistsPublic(SpecialistsBase):
    specialist_id: int
    created_at: datetime
    updated_at: datetime

class SpecialistsUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    birthday: date | None = None
    state: str | None = None
    city: str | None = None
    speciality: str | None = None

class Specialists(SpecialistsBase, table=True):
    specialist_id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())

    patients: list["Patients"] = Relationship(back_populates="specialist")
    tracking_records: list["TrackingRecords"] = Relationship(back_populates="specialist")

""" PATIENTS-COMMORBIDITIES JOIN MODEL """
class PatientComorbidities(SQLModel, table=True):
    patient_id: int = Field(default=None, foreign_key="patients.patient_id", primary_key=True)
    comorbidity_id: int = Field(default=None, foreign_key="comorbidities.comorbidity_id", primary_key=True)

""" COMORBIDITIES TABLES """
class ComorbiditiesBase(SQLModel):
    cid11_code: str | None = None # For now, this field can be optional.
    name: str

class ComorbiditiesCreate(ComorbiditiesBase):
    pass

class ComorbiditiesPublic(ComorbiditiesBase):
    comorbidity_id: int

class ComorbiditiesUpdate(SQLModel):
    cid11_code: str | None = None
    name: str | None = None

class Comorbidities(ComorbiditiesBase, table=True):
    comorbidity_id: int = Field(default=None, primary_key=True)

    patients: list["Patients"] = Relationship(back_populates="comorbidities", link_model=PatientComorbidities)

""" PATIENTS TABLES """
class PatientsBase(SQLModel):
    name: str
    gender: str
    birthday: date
    email: str
    hospital_registration: str
    phone_number: str
    height: float
    weight: float
    smoke_frequency: str
    drink_frequency: str
    accept_tcle: bool
    specialist_id: int | None = Field(default=None, foreign_key="specialists.specialist_id", nullable=True)

class PatientsCreate(PatientsBase):
    comorbidities: list[int] | None = None
    comorbidities_to_add: list[str] | None = None

class PatientsUpdate(SQLModel):
    name: str | None = None
    gender: str | None = None
    birthday: date | None = None
    email: str | None = None
    hospital_registration: str | None = None
    phone_number: str | None = None
    height: float | None = None
    weight: float | None = None
    smoke_frequency: str | None = None
    drink_frequency: str | None = None
    accept_tcle: bool | None = None
    comorbidities: list[int] | None = None
    comorbidities_to_add: list[str] | None = None

class PatientsPublic(PatientsBase):
    patient_id: int
    created_at: datetime
    updated_at: datetime
    comorbidities: list[ComorbiditiesPublic] = []

class Patients(PatientsBase, table=True):
    patient_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    
    specialist: "Specialists" = Relationship(back_populates="patients") # não sei se ta certo
    comorbidities: list["Comorbidities"] = Relationship(back_populates="patients", link_model=PatientComorbidities)
    wounds: list["Wounds"] = Relationship(back_populates="patient", cascade_delete=True)

""" WOUNDS TABLES """
class WoundsBase(SQLModel):
    wound_region: str
    wound_subregion: str | None = None
    wound_type: str
    start_date: date
    end_date: date | None = None
    patient_id: int = Field(foreign_key="patients.patient_id")

class WoundsCreate(WoundsBase):
    pass

class WoundsUpdate(SQLModel):
    is_active: bool
    end_date: date | None = None

class WoundsPublic(WoundsBase):
    wound_id: int

class Wounds(WoundsBase, table = True):
    wound_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    is_active: bool
    patient: "Patients" = Relationship(back_populates="wounds")

    tracking_records: list["TrackingRecords"] = Relationship(back_populates="wound", cascade_delete=True)

""" TRACKING RECORDS TABLES"""
class TrackingRecordsBase(SQLModel):
    wound_length: int
    wound_width: int
    exudate_amount: str
    exudate_type: str
    tissue_type: str 
    wound_edges: str | None = None
    skin_around_the_wound: str | None = None
    had_a_fever: bool | None = None
    pain_level: str | None = None
    dressing_changes_per_day: str | None = None
    guidelines_to_patient: str | None = None
    extra_notes: str | None = None
    image_id: int
    created_at: date
    wound_id: int = Field(foreign_key="wounds.wound_id")
    specialist_id: int = Field(foreign_key="specialists.specialist_id")

class TrackingRecordsCreate(TrackingRecordsBase):
    pass

class TrackingRecordsUpdate(SQLModel):
    wound_size: float | None = None 
    exudate_amount: str | None = None
    exudate_type: str | None = None
    tissue_type: str | None = None
    wound_edges: str | None = None 
    skin_around_the_wound: str | None = None 
    had_a_fever: bool | None = None
    pain_level: str | None = None
    dressing_changes_per_day: str | None = None
    guidelines_to_patient: str | None = None
    extra_notes: str | None = None
    image_id: int | None = None
    is_active: bool | None = None
    created_at: date

class TrackingRecordsPublic(TrackingRecordsBase):
    tracking_record_id: int
    updated_at: datetime

class TrackingRecords(TrackingRecordsBase, table = True):
    tracking_record_id: int = Field(default=None, primary_key=True)
    updated_at: datetime
    is_active: bool
    wound: Wounds = Relationship(back_populates="tracking_records")
    specialist: Specialists = Relationship(back_populates="tracking_records")

""" DATA MODELS FOR RELATIONSHIPS """
class PatientsPublicWithWounds(PatientsPublic):
    wounds: list[WoundsPublic] = []

class WoundsPublicWithTrackingRecords(WoundsPublic):
    tracking_records: list[TrackingRecordsPublic] = []

class SpecialistsPublicWithTrackingRecords(SpecialistsPublic):
    tracking_records: list[TrackingRecordsPublic] = []

class SpecialistsPublicWithPatients(SpecialistsPublic):
    patients: list[PatientsPublic] = []

""" IMAGES TABLES """
class ImagesBase(SQLModel):
    extension: str

class ImagesCreate(ImagesBase):
    pass

class Images(ImagesBase, table = True):
    image_id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now())
    created_by: int = Field(foreign_key="specialists.specialist_id")
