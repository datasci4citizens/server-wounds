from sqlmodel import create_engine, Session, select

import db.config as config
from schema.schema import Comorbidities, Images, PatientComorbidities, Patients, Specialists, TrackingRecords, Wounds


class Database:
    """Database class to handle database connection and operations"""

    def __init__(self):
        self.engine = create_engine(config.POSTGRES_URL)

    def create_db(self):
        """Create the database and tables that do not exist"""
        Specialists.metadata.create_all(self.engine)
        Patients.metadata.create_all(self.engine)
        Wounds.metadata.create_all(self.engine)
        TrackingRecords.metadata.create_all(self.engine)
        PatientComorbidities.metadata.create_all(self.engine)
        Comorbidities.metadata.create_all(self.engine)
        Images.metadata.create_all(self.engine)

    def create_initial_comorbidities(self, engine):
        """ Create the most commom comorbidities """

        session = Session(engine)
        
        existing_comorbidities = session.exec(select(Comorbidities)).first()

        if not existing_comorbidities:
            comorbidities = [
                Comorbidities(cid11_code="5A10", name="Diabetes mellitus tipo 1"),
                Comorbidities(cid11_code="5A11", name="Diabetes mellitus tipo 2"),
                Comorbidities(cid11_code="BA00", name="Hipertensão Essencial"),
                Comorbidities(cid11_code="5B81", name="Obesidade"),
                Comorbidities(cid11_code="8B20", name="Acidente vascular cerebral não conhecido se isquêmico ou hemorrágico"),
                Comorbidities(cid11_code="5C80", name="Hiperlipoproteinemia")
            ]

            session.add_all(comorbidities)
            session.commit()

        session.close()


    # Singleton Database instance attribute
    _db_instance = None

    @staticmethod
    def db_engine():
        """Singleton: get the database instance engine or create a new one"""

        if Database._db_instance is None:
            Database._db_instance = Database()
            Database._db_instance.create_db()
            Database._db_instance.create_initial_comorbidities(Database._db_instance.engine)

        return Database._db_instance.engine

    @staticmethod
    def get_session():
        with Session(Database.db_engine()) as session:
            yield session
