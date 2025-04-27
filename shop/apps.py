from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command
import os
import pkgutil
import importlib

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        if os.environ.get('DJANGO_DEVELOPMENT') == '1':  # Only in development
            post_migrate.connect(run_all_management_commands, sender=self)

def run_all_management_commands(sender, **kwargs):
    from shop.management import commands
    try:
        # Dynamically discover all commands in the management/commands folder
        command_modules = [
            name for _, name, _ in pkgutil.iter_modules(commands.__path__)
        ]
        for command in command_modules:
            try:
                call_command(command)
                print(f"Successfully ran management command: {command}")
            except Exception as e:
                print(f"Error running management command '{command}': {e}")
    except Exception as e:
        print(f"Error discovering management commands: {e}")
