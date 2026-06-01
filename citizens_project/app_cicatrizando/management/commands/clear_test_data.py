from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_cicatrizando.models import Provider, Patient, WoundsUser, Wound, Observation

class Command(BaseCommand):
    help = 'Deletes all Patient, Provider, Wound, Observation, and WoundsUser records (excluding superusers) for testing purposes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Confirm deletion without interactive prompt',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING('This will PERMANENTLY DELETE all patients, specialists, wounds, and observations.'))
            confirm = input('Are you sure? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.NOTICE('Operation aborted.'))
                return

        User = get_user_model()
        
        self.stdout.write('Starting cleanup...')
        
        # Capture counts before deletion
        observation_count = Observation.objects.count()
        wound_count = Wound.objects.count()
        provider_count = Provider.objects.count()
        patient_count = Patient.objects.count()
        wounds_user_count = WoundsUser.objects.count()
        user_count = User.objects.exclude(is_superuser=True).count()

        # Delete in order of dependencies
        Observation.objects.all().delete()
        Wound.objects.all().delete()
        Provider.objects.all().delete()
        Patient.objects.all().delete()
        WoundsUser.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted:\n'
            f'- {observation_count} Observations\n'
            f'- {wound_count} Wounds\n'
            f'- {provider_count} Providers\n'
            f'- {patient_count} Patients\n'
            f'- {wounds_user_count} WoundsUsers\n'
            f'- {user_count} Users'
        ))
