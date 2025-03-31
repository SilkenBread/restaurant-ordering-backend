import time
import redis
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Wait for Redis to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for Redis...')
        max_retries = 10
        retry_delay = 5
        
        for i in range(max_retries):
            try:
                r = redis.Redis(
                    host='redis',
                    port=6379,
                    socket_connect_timeout=1
                )
                r.ping()
                self.stdout.write(self.style.SUCCESS('Redis is available!'))
                return
            except redis.ConnectionError:
                self.stdout.write(f'Attempt {i+1}/{max_retries}: Redis not ready, waiting {retry_delay}s...')
                time.sleep(retry_delay)
        
        self.stdout.write(self.style.ERROR('Could not connect to Redis after multiple attempts'))
        exit(1)
