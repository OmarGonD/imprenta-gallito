import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.services.brevo_service import BrevoService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_brevo():
    print("Testing Brevo Configuration...")
    api_key = settings.BREVO_API_KEY
    
    # Check for quotes
    if api_key.startswith('"') and api_key.endswith('"'):
        print("WARNING: API Key has surrounding quotes! This might be the issue.")
        print(f"Key start: {api_key[:5]}...")
    else:
        print("API Key format seems clean (no surrounding quotes).")
        print(f"Key start: {api_key[:5]}...")
        
    print(f"Sender Email: {settings.BREVO_SENDER_EMAIL}")
    print(f"Sender Name: {settings.BREVO_SENDER_NAME}")

    # Try to find a user to test with, or create a dummy object
    user = User.objects.first()
    if not user:
        print("No users found to test with.")
        return

    print(f"Attempting to send email to: {user.email}")
    
    # Mock request object since we need it for get_current_site
    from unittest.mock import MagicMock
    request = MagicMock()
    request.get_host.return_value = 'localhost:8000'
    request.is_secure.return_value = False
    
    try:
        success = BrevoService.send_activation_email(user, request)
        if success:
            print("SUCCESS: BrevoService returned True.")
        else:
            print("FAILURE: BrevoService returned False.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_brevo()
