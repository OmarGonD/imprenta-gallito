from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Creates placeholder SocialApps for Google and Facebook if they do not exist'

    def handle(self, *args, **kwargs):
        site = Site.objects.get_current()
        providers = ['google', 'facebook']
        
        for provider in providers:
            app, created = SocialApp.objects.get_or_create(
                provider=provider,
                defaults={
                    'name': f'{provider.capitalize()} Login',
                    'client_id': 'placeholder_client_id',
                    'secret': 'placeholder_secret',
                }
            )
            
            if created:
                app.sites.add(site)
                self.stdout.write(self.style.SUCCESS(f'Created {provider} app'))
            else:
                if site not in app.sites.all():
                    app.sites.add(site)
                    self.stdout.write(self.style.SUCCESS(f'Added current site to {provider} app'))
                else:
                    self.stdout.write(self.style.WARNING(f'{provider} app already exists and is configured'))
