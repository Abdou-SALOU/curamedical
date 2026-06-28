# MedPredict — Améliorations identifiées

> Analyse complète du projet au 2026-05-10.
> Chaque point indique le fichier concerné, le problème exact et la solution recommandée.

---

## 🔴 Priorité critique

### 1. Terminer le refacto `useListPage`

**Problème :** Le hook [`frontend/src/hooks/useListPage.js`](frontend/src/hooks/useListPage.js) a été créé mais jamais appliqué aux pages existantes. Chaque page répète ~40 lignes identiques de fetch / search / pagination.

**Fichiers concernés :**
- [`frontend/src/pages/PatientsPage.jsx`](frontend/src/pages/PatientsPage.jsx)
- [`frontend/src/pages/ConsultationsPage.jsx`](frontend/src/pages/ConsultationsPage.jsx)
- [`frontend/src/pages/PrescriptionsPage.jsx`](frontend/src/pages/PrescriptionsPage.jsx)
- [`frontend/src/pages/AppointmentsPage.jsx`](frontend/src/pages/AppointmentsPage.jsx)

**Solution :**
```js
// Remplacer les 40 lignes de fetch/state/useEffect par :
const { data: patients, loading, search, setSearch,
        handleSearch, page, setPage, total, refetch } =
  useListPage('/api/patients/', { pageSize: 20 })
```

---

### 2. JWT stocké dans `localStorage` — Vulnérabilité XSS

**Problème :** Le token JWT est lu et écrit dans `localStorage`
([`frontend/src/api/axios.js:10`](frontend/src/api/axios.js)),
ce qui le rend accessible à tout script injecté (XSS).

**Solution recommandée :**
- Stocker l'`access_token` uniquement **en mémoire** (Zustand store)
- Stocker le `refresh_token` dans un **cookie `httpOnly`** (inaccessible au JS)
- Côté backend : ajouter un endpoint `POST /api/auth/logout/` qui invalide le cookie

```js
// authStore.js — access token en mémoire uniquement
login: async (username, password) => {
  const { data } = await api.post('/api/auth/login/', { username, password })
  // NE PAS mettre dans localStorage
  set({ accessToken: data.access, user: ..., isAuthenticated: true })
}
```

---

### 3. Requêtes N+1 — `select_related` manquant

**Problème :** Les vues Django retournent des listes sans jointures SQL. Pour chaque ligne du tableau, Django fait une requête supplémentaire pour récupérer le patient, le médecin, etc. Sur 20 rendez-vous = potentiellement 60 requêtes au lieu de 1.

**Fichiers concernés :**
- [`backend/apps/appointments/views.py`](backend/apps/appointments/views.py)
- [`backend/apps/consultations/views.py`](backend/apps/consultations/views.py)
- [`backend/apps/prescriptions/views.py`](backend/apps/prescriptions/views.py)

**Solution :**
```python
# Dans chaque ListAPIView / ViewSet
def get_queryset(self):
    return Appointment.objects.select_related(
        'patient', 'doctor'
    ).filter(is_archived=False)
```

---

### 4. Appliquer les migrations après les changements de modèles

**Problème :** Le statut `'demande'` a été ajouté dans `Appointment.STATUS_CHOICES` et des index ont été ajoutés sur `Patient` et `Appointment`, mais les migrations correspondantes n'ont pas été générées ni appliquées.

**Commandes à exécuter :**
```bash
# Via Makefile
make migrate

# Ou directement
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

---

## 🟠 Priorité importante

### 5. `page_size=1000` dans les dropdowns des formulaires

**Problème :** Les formulaires de création chargent massivement toutes les données pour remplir les `<select>` :

| Fichier | Requête problématique |
|---------|----------------------|
| [`ConsultationsPage.jsx:82`](frontend/src/pages/ConsultationsPage.jsx) | `GET /api/appointments/?page_size=1000` |
| [`PrescriptionsPage.jsx:103`](frontend/src/pages/PrescriptionsPage.jsx) | `GET /api/consultations/?page_size=1000` |
| [`AppointmentsPage.jsx:107`](frontend/src/pages/AppointmentsPage.jsx) | `GET /api/patients/?page_size=1000` |

**Solution :** Remplacer les `<select>` par un champ de recherche avec debounce + chargement à la demande (autocomplete).

```jsx
// Exemple : recherche patients dans le formulaire RDV
const [patientSearch, setPatientSearch] = useState('')
const debouncedPatient = useDebounce(patientSearch, 350)
// Charge seulement les 10 premiers résultats correspondants
const { data: patients } = useListPage('/api/patients/',
  { extraParams: { search: debouncedPatient, page_size: 10 } }
)
```

---

### 6. Emails envoyés de façon synchrone (bloque la requête)

**Problème :** Les signaux Django envoient les emails directement dans le thread HTTP. Si le serveur SMTP est lent ou indisponible, l'utilisateur attend (ou reçoit une erreur).

**Fichiers concernés :**
- [`backend/apps/appointments/signals.py`](backend/apps/appointments/signals.py)
- [`backend/apps/prescriptions/signals.py`](backend/apps/prescriptions/signals.py)

**Solution :** Utiliser **Celery** avec Redis comme broker pour les tâches asynchrones.

```bash
# Ajouter à requirements.txt
celery>=5.3
redis>=5.0
```

```python
# tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_appointment_confirmation(patient_email, appointment_date):
    send_mail(subject='Confirmation RDV', ...)

# signals.py — appel non bloquant
send_appointment_confirmation.delay(patient.email, appointment.scheduled_at)
```

---

### 7. Page Audit Logs manquante dans l'interface admin

**Problème :** `django-auditlog` est configuré et enregistre toutes les modifications sur `User`, `Patient`, `Consultation`, `Prescription`, mais aucune interface frontend ne permet de les consulter. L'`AdminPage` ne montre que les utilisateurs.

**Solution :** Créer une section dans [`frontend/src/pages/AdminPage.jsx`](frontend/src/pages/AdminPage.jsx) qui interroge les logs via un endpoint dédié :

```python
# backend : endpoint audit logs
GET /api/audit-logs/?page=1&object_type=Patient
```

```jsx
// frontend : onglet "Journal d'audit" dans AdminPage
const { data: logs } = useListPage('/api/audit-logs/')
```

---

### 8. Throttle spécifique sur l'endpoint IA

**Problème :** `POST /api/consultations/ia/suggest/` utilise le throttle global (`300/minute` par user). Le service Flask peut être saturé par des appels répétés depuis plusieurs onglets.

**Fichiers concernés :**
- [`backend/curamedical/settings.py`](backend/curamedical/settings.py)
- [`backend/apps/consultations/views.py`](backend/apps/consultations/views.py)

**Solution :**
```python
# settings.py
'DEFAULT_THROTTLE_RATES': {
    'anon': '30/minute',
    'user': '300/minute',
    'ia_suggest': '10/minute',   # ← throttle dédié IA
}

# views.py — sur la vue IA
from rest_framework.throttling import ScopedRateThrottle

class IASuggestView(APIView):
    throttle_scope = 'ia_suggest'
```

---

## 🟡 Utile

### 9. Aucun test dans le projet

**Problème :** Zéro fichier de test. Les changements de code ne sont pas vérifiés automatiquement.

**Tests prioritaires à écrire :**

| Test | Framework | Ce qu'il vérifie |
|------|-----------|-----------------|
| Anti-conflit horaire RDV | `pytest-django` | Deux RDV au même créneau → erreur 400 |
| Permissions RBAC | `pytest-django` | Un patient ne peut pas accéder à `/api/patients/` d'un autre |
| `useDebounce` hook | `Vitest` | Le callback n'est appelé qu'après le délai |
| `ConfirmModal` | `Vitest + RTL` | Le bouton Confirmer appelle `onConfirm` |

```bash
# Ajouter à requirements.txt backend
pytest>=7.4
pytest-django>=4.7
factory-boy>=3.3     # fixtures de test

# Ajouter à package.json frontend
"vitest": "^1.0",
"@testing-library/react": "^14.0"
```

---

### 10. CI/CD — Aucun pipeline automatisé

**Problème :** Pas de GitHub Actions. Chaque push peut casser le projet sans qu'on le sache.

**Solution :** Créer `.github/workflows/ci.yml` :

```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker-compose build backend
      - run: docker-compose run backend pytest

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm install && npm run lint
```

---

### 11. `Makefile` non compatible Windows nativement

**Problème :** Le `Makefile` créé nécessite `make` (GNU), non disponible par défaut sur Windows.

**Solution :** Ajouter des scripts PowerShell équivalents dans un dossier `scripts/` :

```
scripts/
  up.ps1          → docker-compose up -d
  down.ps1        → docker-compose down
  logs.ps1        → docker-compose logs -f
  migrate.ps1     → docker-compose exec backend python manage.py migrate
  shell.ps1       → docker-compose exec backend sh
```

---

### 12. Versioning de l'API manquant

**Problème :** Toutes les routes sont `/api/...` sans version. Impossible de faire évoluer l'API en cassant la compatibilité sans impacter les clients existants.

**Solution :**
```python
# urls.py
urlpatterns = [
    path('api/v1/patients/', include('apps.patients.urls')),
    # ...
]
```

```js
// constants.js frontend
export const API = {
  PATIENTS: '/api/v1/patients/',
  // ...
}
```

---

## 🟢 Nice-to-have

### 13. Notifications in-app

**Problème :** Les seules notifications sont par email (n8n). Aucun badge, aucune cloche dans l'interface pour informer l'utilisateur d'un nouveau RDV ou d'une mise à jour de statut.

**Solution :** Ajouter un endpoint de notifications non lues + badge dans la `Navbar` :
```
GET /api/notifications/?is_read=false
```
Badge rouge sur l'icône `event_available` dans la sidebar quand `count > 0`.

---

### 14. Filtre médecin par spécialité dans la prise de RDV

**Problème :** Le `<select>` du médecin dans le formulaire de RDV liste tous les médecins du cabinet sans aucun filtre. Avec 20 médecins de spécialités différentes, c'est confus pour le patient.

**Solution :**
```jsx
// Deux selects en cascade
<select onChange={e => setSpecialty(e.target.value)}>
  {SPECIALTIES.map(s => <option key={s}>{s}</option>)}
</select>

<select value={form.doctor}>
  {doctors.filter(d => d.specialty === specialty).map(d => (
    <option key={d.id} value={d.id}>Dr. {d.last_name}</option>
  ))}
</select>
```

---

### 15. Page 404 manquante

**Problème :** La route `*` dans [`frontend/src/App.jsx`](frontend/src/App.jsx) redirige silencieusement vers `/` sans informer l'utilisateur que la page n'existe pas.

**Solution :** Créer `frontend/src/pages/NotFoundPage.jsx` et l'afficher sur `*` au lieu de `<Navigate to="/" />`.

---

## Récapitulatif

| # | Amélioration | Priorité | Effort | Impact |
|---|-------------|----------|--------|--------|
| 1 | Refacto `useListPage` | 🔴 Critique | Moyen | Maintenabilité |
| 2 | JWT → mémoire + httpOnly cookie | 🔴 Critique | Élevé | Sécurité |
| 3 | `select_related` N+1 | 🔴 Critique | Faible | Performance |
| 4 | Lancer les migrations | 🔴 Critique | Très faible | Fonctionnel |
| 5 | Supprimer `page_size=1000` | 🟠 Important | Moyen | Performance |
| 6 | Emails async avec Celery | 🟠 Important | Élevé | Fiabilité |
| 7 | Page Audit Logs frontend | 🟠 Important | Moyen | Fonctionnel |
| 8 | Throttle endpoint IA | 🟠 Important | Faible | Sécurité |
| 9 | Tests (pytest + Vitest) | 🟡 Utile | Élevé | Qualité |
| 10 | CI/CD GitHub Actions | 🟡 Utile | Moyen | DevEx |
| 11 | Scripts PowerShell Windows | 🟡 Utile | Faible | DevEx |
| 12 | Versioning API `/v1/` | 🟡 Utile | Faible | Architecture |
| 13 | Notifications in-app | 🟢 Nice | Élevé | UX |
| 14 | Filtre médecin par spécialité | 🟢 Nice | Faible | UX |
| 15 | Page 404 | 🟢 Nice | Très faible | UX |

---

*Généré le 2026-05-10 — MedPredict v2*
