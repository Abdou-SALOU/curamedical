import requests
import os
from decouple import config

# URL du service IA (récupérée du .env ou localhost par défaut)
IA_SERVICE_URL = config('IA_SERVICE_URL', default='http://localhost:5005')

def obtenir_suggestions_ia(symptomes: list, age: int = 30, 
                            genre: str = 'Male', tension: str = 'Normal', 
                            cholesterol: str = 'Normal') -> list:
    """
    Appelle le service Flask pour obtenir des suggestions de diagnostic.
    """
    try:
        response = requests.post(
            f"{IA_SERVICE_URL}/predict",
            json={
                'symptoms': symptomes,
                'age': age,
                'genre': genre,
                'tension': tension,
                'cholesterol': cholesterol,
                'outcome': 'Positive'
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json().get('suggestions', [])
        else:
            print(f"Erreur IA Service: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion au service IA: {e}")
        
    return []
