import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Wait for database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        max_retries = 20
        retry_delay = 5
        
        for i in range(max_retries):
            try:
                connections['default'].ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database is available!'))
                return
            except OperationalError:
                self.stdout.write(f'Attempt {i+1}/{max_retries}: Database not ready, waiting {retry_delay}s...')
                time.sleep(retry_delay)
        
        self.stdout.write(self.style.ERROR('Could not connect to database after multiple attempts'))
        exit(1)
