from django.core.management.base import BaseCommand
from realestate.models import Gift


class Command(BaseCommand):
    help = 'Set up default gifts for the reward system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up default gifts...')
        
        # Create default gifts
        Gift.create_default_gifts()
        
        # Display created gifts
        gifts = Gift.objects.all().order_by('required_star_level')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {gifts.count()} gifts:'))
        for gift in gifts:
            self.stdout.write(f'  • {gift.name} (Level {gift.required_star_level}) - {gift.description}')
        
        self.stdout.write(self.style.SUCCESS('Default gifts setup complete!'))
