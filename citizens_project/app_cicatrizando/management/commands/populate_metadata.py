#esse comando nao esta funcionando devido a problema de circularidade entre as tabelas
#Domain, Vocabulary, ConceptClass e Concept.
#olhar o comentario no arquivo add_comorbidity_icd10.py

'''
import pandas as pd
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Import all relevant OMOP models
from app_cicatrizando.omop.omop_models import Concept, Domain, ConceptClass, Vocabulary

class Command(BaseCommand):
    help = 'Populates essential OMOP CDM metadata tables (ConceptClass, Vocabulary, Concept metadata, Domain).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting OMOP CDM metadata population...")

        # --- Data Definitions for OMOP Metadata ---

        # 1. Concept Classes to be added
        concept_classes_data = [
            ('Domain', 'Domain'),
            ('Vocabulary', 'Vocabulary'),
            ('Standard', 'Standard'),
            ('Metadata', 'Metadata'),
            ('Condition', 'Condition'), # Will be used for 'Condition' concept_class
            ('Type Concept', 'Type Concept'), # Often used for various type concepts
        ]
        
        # 2. Vocabularies to be added
        vocabularies_data = [
            ('OMOP Domain', 'OMOP Domain'),
            ('Standard', 'Standard'),
            ('ICD10', 'ICD-10 Classification'),
            ('SNOMED', 'SNOMED Clinical Terms'),
            # Add other necessary vocabularies based on your full CONCEPT.csv if needed
        ]

        # 3. Core Metadata Concepts (that Do#main, Vocabulary, ConceptClass FKs point to)
        # (concept_id, concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept, concept_code)
        # Note: The domain_id, vocabulary_id, concept_class_id here must exist AFTER their respective tables are populated.
        # But for 'Metadata' concepts, their own FKs often point to 'Metadata', 'OMOP Domain', 'Domain' etc.
        core_metadata_concepts_data = [
            # Concepts for Domains
            (21, 'Condition', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Condition'),
            (27, 'Observation', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Observation'),
            (13, 'Drug', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Drug'),
            (19, 'Measurement', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Measurement'),
            (10, 'Procedure', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Procedure'),
            (14, 'Device', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Device'),
            (17, 'Death', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Death'),
            (8, 'Gender', 'Metadata', 'OMOP Domain', 'Domain', 'S', 'Gender'),
            
            # Concepts for Vocabularies
            (44819131, 'OMOP Standard Vocabularies', 'Metadata', 'OMOP Standard Vocabularies', 'Vocabulary', 'S', 'OMOP Standard Vocabularies'),
            # You might need specific concept_ids for 'ICD10' or 'SNOMED' vocabularies if they reference Concept.
            # For simplicity, if your Vocabulary model FK to Concept allows null, we can skip it for now or provide dummy.
            
            # Concepts for Concept Classes
            (44819129, 'Metadata domain', 'Metadata', 'OMOP Domain', 'Concept Class', 'S', 'Metadata'),
            (44819128, 'Type Concept domain', 'Metadata', 'OMOP Domain', 'Concept Class', 'S', 'Type Concept'),
            (44819130, 'Domain concept', 'Metadata', 'OMOP Domain', 'Concept Class', 'S', 'Domain'),
            (44819132, 'Vocabulary concept', 'Metadata', 'OMOP Domain', 'Concept Class', 'S', 'Vocabulary'),
            (44819133, 'Concept Class concept', 'Metadata', 'OMOP Domain', 'Concept Class', 'S', 'Concept Class'),
            # Add more metadata concepts as found in your official OMOP CONCEPT.csv
        ]

        # --- STEP 1: Populate ConceptClass table ---
        self.stdout.write("\nPopulating ConceptClass table...")
        for cc_id, cc_name in concept_classes_data:
            obj, created = ConceptClass.objects.get_or_create(
                concept_class_id=cc_id,
                defaults={
                    'concept_class_name': cc_name,
                    'concept_class_concept': None # Temporarily None, will be updated if needed or left as null
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"ConceptClass '{cc_name}' (ID: {cc_id}) created."))
            else:
                self.stdout.write(f"ConceptClass '{cc_name}' (ID: {cc_id}) already exists.")

        # --- STEP 2: Populate Vocabulary table ---
        self.stdout.write("\nPopulating Vocabulary table...")
        for vocab_id, vocab_name in vocabularies_data:
            obj, created = Vocabulary.objects.get_or_create(
                vocabulary_id=vocab_id,
                defaults={
                    'vocabulary_name': vocab_name,
                    'vocabulary_reference': None,
                    'vocabulary_version': None,
                    'vocabulary_concept': None # Temporarily None
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Vocabulary '{vocab_name}' (ID: {vocab_id}) created."))
            else:
                self.stdout.write(f"Vocabulary '{vocab_name}' (ID: {vocab_id}) already exists.")

        # --- STEP 3: Populate core metadata Concepts table ---
        # These concepts are critical as they are referenced by Domain, Vocabulary, and ConceptClass tables.
        self.stdout.write("\nPopulating core metadata Concepts table...")
        for c_id, c_name, d_id, v_id, cc_id, std_concept, c_code in core_metadata_concepts_data:
            # Ensure domain, vocabulary, concept_class for these concepts exist (which they should after steps 1 & 2)
            try:
                # Retrieve existing related objects or handle their absence if necessary
                domain_obj = Domain.objects.get(domain_id=d_id) if d_id else None
                vocabulary_obj = Vocabulary.objects.get(vocabulary_id=v_id) if v_id else None
                concept_class_obj = ConceptClass.objects.get(concept_class_id=cc_id) if cc_id else None

                obj, created = Concept.objects.get_or_create(
                    concept_id=c_id,
                    defaults={
                        'concept_name': c_name,
                        'domain': domain_obj, # This is now a FK
                        'vocabulary': vocabulary_obj, # This is now a FK
                        'concept_class': concept_class_obj, # This is now a FK
                        'standard_concept': std_concept,
                        'concept_code': c_code,
                        'valid_start_date': '1970-01-01',
                        'valid_end_date': '2099-12-31',
                        'invalid_reason': None
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Metadata Concept '{c_name}' (ID: {c_id}) created."))
                else:
                    self.stdout.write(f"Metadata Concept '{c_name}' (ID: {c_id}) already exists.")
            except (Domain.DoesNotExist, Vocabulary.DoesNotExist, ConceptClass.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(f"Error creating Concept {c_id} ({c_name}): Related object missing: {e}. Check steps 1 & 2 and your data."))
                continue

        # --- STEP 4: Populate Domain table (can now reference Concepts) ---
        self.stdout.write("\nPopulating Domain table...")
        for domain_id, domain_name, domain_concept_id, _ in domains_and_metadata:
            try:
                # Retrieve the concept that this domain's domain_concept FK will point to
                domain_concept_obj = Concept.objects.get(concept_id=domain_concept_id)
                obj, created = Domain.objects.get_or_create(
                    domain_id=domain_id,
                    defaults={
                        'domain_name': domain_name,
                        'domain_concept': domain_concept_obj # Now this FK can be set
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Domain '{domain_name}' (ID: {domain_id}) created."))
                else:
                    self.stdout.write(f"Domain '{domain_name}' (ID: {domain_id}) already exists.")
            except Concept.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Error creating Domain '{domain_name}': domain_concept_id {domain_concept_id} not found in Concept table. Check Step 3."))
                continue

 '''