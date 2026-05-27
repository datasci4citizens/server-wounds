import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from app_cicatrizando.models import Comorbidity

class Command(BaseCommand):
    help = 'Populates the Comorbidity database with contents from cid11.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='cid11.csv',
            help='Path to the cid11.csv file'
        )

    def handle(self, *args, **options):
        # Default to the root directory where cid11.csv is located
        file_path = options['file']
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR.parent, file_path)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found at {file_path}'))
            return

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
                    
                concept_id = lin_uri
                
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
