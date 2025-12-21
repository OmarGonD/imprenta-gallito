import base64
import json
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

def check_key():
    raw_key = settings.BREVO_API_KEY
    print(f"Raw key from settings: {raw_key[:10]}...")
    
    try:
        # Try decoding base64
        decoded_bytes = base64.b64decode(raw_key)
        decoded_str = decoded_bytes.decode('utf-8')
        print(f"Decoded string: {decoded_str}")
        
        # Try parsing JSON
        data = json.loads(decoded_str)
        if 'api_key' in data:
            print(f"FOUND REAL KEY: {data['api_key']}")
            return True
    except Exception as e:
        print(f"Not a base64 encoded json: {e}")
        
    return False

if __name__ == "__main__":
    check_key()
