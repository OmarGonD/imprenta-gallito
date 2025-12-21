import base64
import json
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from shop.tokens import account_activation_token


class BrevoService:
    @staticmethod
    def _get_api_key():
        """Retrieve and clean the API key, handling potential base64 encoding errors."""
        api_key = settings.BREVO_API_KEY
        if not api_key:
            print("[BREVO ERROR] No API key configured!")
            return None
            
        # Check if it looks like the base64 encoded JSON (starts with eyJ)
        if api_key.startswith('eyJ'):
            try:
                decoded_bytes = base64.b64decode(api_key)
                decoded_str = decoded_bytes.decode('utf-8')
                data = json.loads(decoded_str)
                if 'api_key' in data:
                    print(f"[BREVO] API Key decoded successfully (starts with: {data['api_key'][:10]}...)")
                    return data['api_key']
            except Exception as e:
                print(f"[BREVO WARNING] Failed to decode API key as base64: {e}")
                pass
        
        return api_key

    @staticmethod
    def send_activation_email(user, request):
        """
        Sends an activation email to the user using Brevo API.
        """
        print("=" * 60)
        print("[BREVO] Iniciando envío de correo de activación...")
        print(f"[BREVO] Usuario: {user.username}")
        print(f"[BREVO] Correo destino: {user.email}")
        print("=" * 60)
        
        configuration = sib_api_v3_sdk.Configuration()
        api_key = BrevoService._get_api_key()
        
        if not api_key:
            print("[BREVO ERROR] API Key no configurada. No se puede enviar el correo.")
            return False
            
        configuration.api_key['api-key'] = api_key

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        current_site = get_current_site(request)
        mail_subject = 'Activa tu cuenta de Imprenta Gallito'
        
        # Prepare context data
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        domain = current_site.domain
        
        print(f"[BREVO] Dominio: {domain}")
        print(f"[BREVO] UID: {uid}")
        print(f"[BREVO] Token: {token[:20]}...")
        
        # Render the HTML content
        html_content = render_to_string('accounts/acc_activate_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
        })
        
        # Configure the sender and recipient
        sender = {"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL}
        to = [{"email": user.email, "name": user.username}]
        
        print(f"[BREVO] Remitente: {sender['name']} <{sender['email']}>")
        print(f"[BREVO] Destinatario: {to[0]['name']} <{to[0]['email']}>")
        
        # Create the email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=mail_subject,
            html_content=html_content
        )

        try:
            print("[BREVO] Enviando correo via API...")
            api_response = api_instance.send_transac_email(send_smtp_email)
            print("=" * 60)
            print(f"[BREVO SUCCESS] ¡Correo enviado exitosamente!")
            print(f"[BREVO SUCCESS] Message ID: {api_response}")
            print(f"[BREVO SUCCESS] Enviado a: {user.email}")
            print("=" * 60)
            return True
        except ApiException as e:
            print("=" * 60)
            print(f"[BREVO ERROR] Fallo al enviar correo a: {user.email}")
            print(f"[BREVO ERROR] Excepción: {e}")
            print("=" * 60)
            return False

