# 🏥 CuraMedical — Gestion Intelligente de Cabinet Médical

Application de gestion de cabinet médical avec module d'assistance 
au diagnostic par intelligence artificielle.

## 🏗️ Architecture
```
curamedical/
├── backend/       → Django + DRF (API REST)
├── frontend/      → React + Vite (Interface utilisateur)
├── ia-service/    → Flask + Scikit-learn (Microservice IA)
└── docker-compose.yml
```

## ⚙️ Prérequis

- Docker Desktop
- Python 3.11+
- Node.js 20+
- Git

## 🚀 Lancement rapide

### 1. Cloner le projet
```bash
git clone https://github.com/VOTRE_USERNAME/curamedical.git
cd curamedical
```

### 2. Configurer les variables d'environnement
```bash
cp .env.example .env
# Modifiez .env avec vos valeurs
```

### 3. Entraîner le modèle IA
```bash
cd ia-service
python -m venv venv-ai
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train.py
cd ..
```

### 4. Lancer avec Docker
```bash
docker-compose up --build
```

### 5. Initialiser la base de données
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py init_accounts
```

## 🌐 Accès aux services

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API Django | http://localhost:8000/api |
| Admin Django | http://localhost:8000/admin |
| Microservice IA | http://localhost:5000 |

| Rôle | Login / Pass | Accès |
|---|---|---|
| Administrateur | admin / adminpassword | Configuration, Utilisateurs, Audit |
| Médecin | medecin / medecinpassword | Consultations, Ordonnances, IA |
| Secrétaire | secretaire / secretairepassword | Patients, RDV, Planning |
| Patient | (via inscription) | Espace personnel, RDV, Ordonnances |

## 🧪 Backend — Environnement local
```bash
cd backend
python -m venv venv-backend
source venv/bin/activate
pip install -r requirements.txt
```

## 🤖 IA Service — Environnement local
```bash
cd ia-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train.py
```

## 📋 Stack technique

- **Backend** : Django 4.2 + Django REST Framework
- **Base de données** : PostgreSQL 15
- **Frontend** : React + Vite + Tailwind CSS
- **IA** : Flask + Scikit-learn (Random Forest)
- **Auth** : JWT (SimpleJWT)
- **Conteneurisation** : Docker + Docker Compose

## 📁 Programme IABD 2025-2026