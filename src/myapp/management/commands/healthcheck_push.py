from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from time import sleep
from datetime import datetime
import random
import io
from django.core.cache import cache, caches

class Command(BaseCommand):
    help = 'Health check push worker'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS(f'Starting Health-check push Worker.'))

        while True:
            # Always pull config values from django-solo

            start = datetime.now().strftime('%s')

            # TODO: Logic to decide if/what/how to push a status health check to some place
            self.stdout.write(self.style.SUCCESS(f'Pushed health status'))

            # TODO: Pull sleep interval from django solo
            sleep(5)