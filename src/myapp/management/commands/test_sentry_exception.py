from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Raise an unhandled exception to show up in sentry'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS(f'Raising unhandled exception for Sentry...'))
        raise Exception('Check for this in Sentry...')