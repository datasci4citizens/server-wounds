import os
import csv
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from app_cicatrizando.models import Comorbidity

comorbidity_max_name_length = Comorbidity._meta.get_field("name").max_length

### This script is populating the database with ICD-11, and not with OMOP CDM.


class Command(BaseCommand):
    'Populates the Comorbidity database with contents from comorbidities_ICD11.csv'

    def add_arguments(self, parser):
        # Determine default path relative to this file's location
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_csv = os.path.join(current_dir, 'comorbidities_ICD11.csv')
        
        parser.add_argument(
            '--file',
            type=str,
            default=default_csv,
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Repopulate comorbidities even if the table already has records. Use when new comorbidities need to be added',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        force = options['force']
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR.parent, file_path)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found at {file_path}'))
            return

        if Comorbidity.objects.exists() and not force:
            self.stdout.write(self.style.WARNING('Comorbidity table already has records. Skipping population.'))
            return

        if Comorbidity.objects.exists() and force:
            self.stdout.write(self.style.WARNING('Repopulating comorbidities table.'))
            Comorbidity.objects.all().delete()

        self.stdout.write(self.style.NOTICE('Starting population of comorbidities...'))
        
        batch_size = 5000
        objs = []
        seen_ids = set()

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                lin_uri = row.get('Linearization URI', '').strip()
                if not lin_uri:
                    continue
                    
                concept_matches = re.findall(r'(\d+)', lin_uri)
                if not concept_matches:
                    continue
                concept_id = concept_matches[-1]
                
                if concept_id in seen_ids:
                    continue
                seen_ids.add(concept_id)

                title = row.get('Title', '').strip()
                if not title:
                    title = row.get('TitleEN', '').strip()
                    
                # Remove leading dashes and spaces
                title = title.lstrip('- ')
                title = title[:255]
                
                code = row.get('Code', '').strip() or None
                
                objs.append(Comorbidity(concept_id=concept_id, code=code, name=title))
                
                if len(objs) >= batch_size:
                    Comorbidity.objects.bulk_create(objs, ignore_conflicts=True)
                    self.stdout.write(self.style.SUCCESS(f'Processed {len(seen_ids)} records...'))
                    objs = []
                    
            if objs:
                Comorbidity.objects.bulk_create(objs, ignore_conflicts=True)
                
        self.stdout.write(self.style.SUCCESS(f'Successfully populated {Comorbidity.objects.count()} comorbidities!'))
