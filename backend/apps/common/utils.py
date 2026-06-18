import requests
import json
import base64
from django.conf import settings

def send_to_n8n_automation(data, binary_data=None, filename=None):
    """Envoie les données et éventuellement un binaire au webhook n8n."""
    url = getattr(settings, 'N8N_WEBHOOK_URL', None)
    if not url:
        print("n8n Webhook URL non configuré.")
        return False
    
    payload = {
        "event": data.get("event"),
        "patient": data.get("patient_name"),
        "email": data.get("patient_email"),
        "patient_tel": data.get("patient_tel"),
        "doctor": data.get("doctor_name"),
        "date": data.get("date"),
        "details": data.get("details"),
    }
    for key, value in data.items():
        if value is not None and key not in payload:
            payload[key] = value
    
    # Si on a un fichier binaire (PDF), on l'encode en base64 pour le webhook
    if binary_data:
        payload["file"] = base64.b64encode(binary_data).decode('utf-8')
        payload["filename"] = filename or "document.pdf"
        
    try:
        print(f"Envoi des données vers n8n: {url}")
        print(f"Taille du payload: {len(json.dumps(payload))} octets")
        response = requests.post(url, json=payload, timeout=15)
        print(f"Réponse n8n: {response.status_code} - {response.text}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi à n8n : {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Détails de l'erreur: {e.response.text}")
        return False
