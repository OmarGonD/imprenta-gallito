from django.core.management.base import BaseCommand
from django.core.management import call_command
import pkgutil
from shop.management import commands

class Command(BaseCommand):
    help = "Run all management commands in the management/commands folder"

    def handle(self, *args, **options):
        self.stdout.write("Discovering and running all management commands...")
        try:
            # Dynamically discover all commands in the management/commands folder
            command_modules = [
                name for _, name, _ in pkgutil.iter_modules(commands.__path__)
                if name != "run_all"  # Exclude this command itself
            ]
            for command in command_modules:
                try:
                    call_command(command)
                    self.stdout.write(self.style.SUCCESS(f"Successfully ran command: {command}"))
                except Exception as e:
                    self.stderr.write(f"Error running command '{command}': {e}")
        except Exception as e:
            self.stderr.write(f"Error discovering commands: {e}")
