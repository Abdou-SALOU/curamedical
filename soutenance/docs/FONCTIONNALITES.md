# MedPredict v2 — Inventaire Complet des Fonctionnalités

> Document de référence pour la reproduction dans MedPredict v1.

---

## Architecture Générale

| Couche | Technologie | Port |
|---|---|---|
| **Backend** | Django REST Framework (Python) | 8000 |
| **Frontend** | React 19 + Vite + TailwindCSS | 3000 / 5173 |
| **Service IA** | Flask (Python) | 5005 |
| **Automatisation** | n8n (workflows) | - |
| **Base de données** | PostgreSQL | - |

---

## 1. Authentification & Gestion des Utilisateurs

| Fonctionnalité | Description |
|---|---|
| Connexion JWT | Access token (8h) + Refresh token (7 jours), rotation activée |
| 4 rôles distincts | Administrateur, Médecin, Secrétaire, Patient |
| Auto-inscription Patient | Crée User + Patient en une seule requête (`/register/`) |
| Changement mot de passe | Par le propriétaire du compte ou l'administrateur |
| Liste des médecins actifs | Accessible à tous les utilisateurs connectés |
| 17 spécialités médicales | généraliste, cardiologue, dermatologue, neurologue, etc. |
| CRUD complet utilisateurs | Réservé à l'administrateur |
| Page Login | Interface avec JWT, présentation des features du projet |
| Page Register | Formulaire d'inscription pour les patients uniquement |

### Permissions personnalisées (8 classes)

| Classe | Règle |
|---|---|
| `EstMedecin` | `role == 'medecin'` |
| `EstSecretaire` | `role == 'secretaire'` |
| `EstAdministrateur` | `role == 'administrateur'` ou `is_superuser` |
| `EstPatient` | `role == 'patient'` |
| `EstMedecinOuSecretaire` | `role in ['medecin', 'secretaire']` |
| `EstStaffOuAdministrateur` | `role in ['medecin', 'secretaire', 'administrateur']` |
| `EstProprietaire` | Vérifie la relation de propriété sur l'objet |

---

## 2. Gestion des Patients

| Fonctionnalité | Description |
|---|---|
| CRUD Patients | Créer, lire, modifier, supprimer |
| Soft Delete (Archivage) | Archive au lieu de supprimer définitivement |
| Patients archivés | Restauration ou consultation par l'admin |
| Identité complète | Nom, prénom, date naissance, sexe (M/F), CIN |
| Contact | Téléphone, email, adresse, ville |
| Dossier médical | Groupe sanguin (8 types : A+, A-, B+, B-, AB+, AB-, O+, O-) |
| Historique médical | Allergies, antécédents médicaux, médicaments en cours |
| Calcul d'âge automatique | Propriété `@property age` calculée dynamiquement |
| Recherche multi-champs | Nom, prénom, CIN, téléphone |
| Filtres avancés | Par groupe sanguin, sexe, ville |
| Stats patients | Total, par sexe, par groupe sanguin |
| Mes infos (patient) | Le patient connecté consulte son propre profil (`/mes-infos/`) |
| Lien compte patient | Liaison OneToOne vers User (optionnel) |
| Audit trail | Toutes les modifications enregistrées via django-auditlog |

---

## 3. Gestion des Rendez-vous

| Fonctionnalité | Description |
|---|---|
| CRUD Rendez-vous | Créer, lire, modifier, supprimer |
| Types de RDV | Présentiel (au cabinet) ou En ligne (téléconsultation vidéo) |
| Statuts multiples | `DEMANDE` → `PLANIFIE` → `CONFIRME` → `EN_COURS` → `TERMINE` / `ANNULE` |
| Durée configurable | En minutes, défaut : 30 min |
| Anti-conflit horaire | Vérification automatique des chevauchements pour un même médecin |
| Génération lien vidéo | UUID Jitsi auto-généré si le RDV est de type EN_LIGNE |
| Vue Calendrier | Interface calendrier interactive (FullCalendar) |
| Vue Liste | Tableau filtrable et recherchable |
| Prise de RDV (patient) | Le patient choisit son médecin, sa date et son heure |
| Mes RDV (médecin) | Le médecin consulte ses rendez-vous à venir |
| Filtres | Par statut, médecin, patient, plage de dates |
| Stats RDV | Taux honoré, taux annulé, répartition par statut |

---

## 4. Gestion des Consultations

| Fonctionnalité | Description |
|---|---|
| CRUD Consultations | Créer, lire, modifier, supprimer |
| Saisie symptômes par tags | Interface de tags avec liste de symptômes suggérés |
| Examen clinique | Champ texte libre |
| Diagnostic retenu | Champ texte libre |
| Notes du médecin | Champ texte libre |
| Lien avec RDV | Association consultation ↔ rendez-vous (optionnel) |
| Lien avec patient | Relation directe avec le dossier patient |
| Suggestions IA | Champ JSON stockant les 3 pathologies proposées |
| Compte rendu PDF | Génération PDF professionnel téléchargeable (`/compte-rendu-pdf/`) |
| Historique dans dossier | Vue complète dans le dossier patient (onglet consultations) |
| Mes consultations (patient) | Le patient consulte l'historique de ses consultations |
| Stats consultations | Par période (semaine/mois), top 10 pathologies |
| Stats utilisation IA | Taux d'utilisation du module IA par le médecin |
| Recherche | Par symptômes, diagnostic, nom/prénom patient |

---

## 5. Module IA — Aide au Diagnostic

| Fonctionnalité | Description |
|---|---|
| Microservice Flask indépendant | Service dédié sur le port 5005 |
| Analyse des symptômes | Entrées : symptômes, âge, genre, tension artérielle, cholestérol |
| Top 3 pathologies | Retourne 3 diagnostics avec leur score de confiance (%) |
| Mapping symptômes FR → EN | Traduction automatique : fièvre → Fever, toux → Cough, etc. |
| Sauvegarde des suggestions | Les suggestions sont stockées dans le champ `suggestions_ia` (JSONField) |
| Indicateur utilisation IA | Champ booléen `ia_utilisee` sur la consultation |
| Avertissement légal | Message affiché : "outil d'aide, ne remplace pas le diagnostic médical" |
| Bouton "Analyser avec l'IA" | Disponible dans le formulaire de consultation ET pendant la vidéo |
| Stats d'utilisation | Taux d'utilisation global accessible aux médecins |
| Entraînement du modèle | Script `train.py` pour ré-entraîner le modèle ML |
| Endpoint santé | `GET /health` pour vérifier la disponibilité du service |

---

## 6. Gestion des Ordonnances (Prescriptions)

| Fonctionnalité | Description |
|---|---|
| CRUD Ordonnances | Créer, lire, modifier, supprimer |
| Lignes de prescription | Liste dynamique de médicaments par ordonnance |
| Par médicament | Nom, dosage (ex : 500mg), unité, fréquence, durée, instructions |
| Unités disponibles | Comprimé, gélule, sachet, ampoule, sirop, gouttes, crème |
| Lien avec consultation | Chaque ordonnance est liée à une consultation (OneToOne) |
| PDF ordonnance | Génération PDF avec tableau médicaments (`/ordonnance-pdf/`) |
| Mes ordonnances (patient) | Le patient télécharge et consulte ses ordonnances |
| Historique médecin | Vue liste de toutes les ordonnances rédigées |
| Recherche | Par nom patient, prénom, ou nom de médicament |

---

## 7. Téléconsultation Vidéo

| Fonctionnalité | Description |
|---|---|
| Intégration Jitsi Meet | Via `@jitsi/react-sdk` (open source, sans serveur dédié) |
| Salle unique par RDV | UUID auto-généré, accessible sur `/consultation/{lien_visio}` |
| Accès sécurisé | Patient + Médecin rejoignent la même salle |
| Panel consultation temps réel | Le médecin saisit la consultation dans un panneau latéral pendant la vidéo |
| Module IA pendant la vidéo | Analyse IA disponible directement pendant la téléconsultation |
| Quitter la consultation | Bouton de déconnexion propre avec nettoyage des listeners |

---

## 8. Notifications & Emails

| Fonctionnalité | Déclencheur | Destinataire |
|---|---|---|
| Email confirmation RDV | Signal `post_save` → statut devient CONFIRME ou PLANIFIE | Patient |
| Rappel 24h avant RDV | n8n — cron quotidien à 8h | Patient |
| Ordonnance disponible | n8n — webhook Django quand statut → TERMINE | Patient |
| Templates HTML | Emails stylisés avec variables dynamiques | - |

---

## 9. Export PDF

### Compte rendu de consultation
- En-tête : médecin, clinique
- Informations patient : nom, âge, sexe, date
- Motif de consultation & symptômes
- Examen clinique, diagnostic, notes
- Pied de page avec signature

### Ordonnance médicale
- En-tête : médecin, clinique
- Informations patient : nom, âge, sexe, date
- Tableau médicaments : nom, dosage, posologie, durée, instructions
- Pied de page avec signature

**Technologie :** ReportLab (Python)

---

## 10. Dashboard & Statistiques

| Rôle | Contenu affiché |
|---|---|
| **Administrateur** | Total patients, RDV, consultations, utilisateurs ; KPIs globaux |
| **Médecin** | RDV du jour, dernières consultations, top pathologies, stats IA |
| **Secrétaire** | RDV à venir, patients récents |
| **Patient** | Mes RDV, mes consultations, mes ordonnances |

### Stats avancées (Médecin / Admin)
- Taux RDV honoré vs annulé
- Top 10 pathologies diagnostiquées
- Consultations par semaine / par mois
- Taux d'utilisation du module IA
- Répartition par statut de RDV

---

## 11. Audit & Sécurité

| Fonctionnalité | Description |
|---|---|
| Audit Log complet | Toutes les modifications enregistrées (django-auditlog) |
| Objets tracés | User, Patient, Consultation, Prescription |
| Vue admin des logs | Historique : utilisateur, action, horodatage, objet modifié |
| Middleware JWT+Audit | Authentification JWT avant logging pour garantir la traçabilité |
| Contrôle d'accès strict | Chaque endpoint vérifie le rôle de l'utilisateur |
| Tokens rotatifs | Refresh token invalidé après usage |

---

## 12. Workflows n8n (Automatisation)

### Workflow 1 — Rappel 24h
| Étape | Action |
|---|---|
| 1. Schedule Trigger | Déclenché chaque matin à 8h |
| 2. Authentification | Récupère le token JWT via `/api/token/` |
| 3. Requête API | Appelle `/appointments/` filtré sur la date du lendemain |
| 4. Itération | Parcourt chaque RDV trouvé |
| 5. Email | Envoie un rappel personnalisé au patient |

### Workflow 2 — RDV Terminé
| Étape | Action |
|---|---|
| 1. Webhook | Reçoit le POST de Django (signal `post_save`, statut → TERMINE) |
| 2. Email | Envoie un email "votre ordonnance est disponible" au patient |

---

## 13. Contrôle d'accès par rôle

| Ressource | Admin | Médecin | Secrétaire | Patient |
|---|---|---|---|---|
| Patients | CRUD complet | Lecture (ses patients) | CRUD | Lecture (ses infos) |
| Rendez-vous | CRUD complet | Lecture (ses RDV) | CRUD complet | CRUD (ses RDV) |
| Consultations | Lecture | CRUD complet | Lecture | Lecture (siennes) |
| Ordonnances | Lecture | CRUD complet | Lecture | Lecture (siennes) |
| Utilisateurs | CRUD complet | — | — | — |
| Audit Logs | Lecture | — | — | — |
| Statistiques | Toutes | Ses stats + top pathologies | Stats RDV | — |
| Module IA | — | Oui | — | — |
| Téléconsultation | — | Oui (panel médecin) | — | Oui (participant) |

---

## 14. Documentation API

| Ressource | URL |
|---|---|
| Schéma OpenAPI (JSON) | `GET /api/schema/` |
| Swagger UI interactif | `GET /api/docs/` |

---

## 15. Résumé Technique

### Backend — Dépendances principales
```
djangorestframework
djangorestframework-simplejwt
django-filter
drf-spectacular
django-cors-headers
django-auditlog
reportlab
requests
python-decouple
psycopg2
```

### Frontend — Dépendances principales
```
react@19
react-router-dom@7
axios
zustand               # State management global
@tanstack/react-query # Cache & fetching données
recharts              # Graphiques statistiques
lucide-react          # Icônes
react-hot-toast       # Notifications toast
@fullcalendar/react   # Calendrier rendez-vous
@jitsi/react-sdk      # Vidéoconférence
tailwindcss@4
vite@8
```

### Configuration Django
| Paramètre | Valeur |
|---|---|
| Authentification | JWT (SimpleJWT) |
| Access Token Lifetime | 8 heures |
| Refresh Token Lifetime | 7 jours |
| Rotation des tokens | Activée |
| Pagination | 20 résultats par défaut |
| Timezone | Africa/Casablanca |
| Langue | Français (fr-fr) |
| Email | SMTP Gmail (ou console en dev) |
| Service IA | `http://ia-service:5000` |

---

## 16. Flux Utilisateur Clés

### Patient — S'inscrire et prendre un RDV
1. Accès à `/register` → Formulaire (username, email, mot de passe, infos personnelles)
2. Création automatique User + Patient
3. Connexion → Redirection vers l'espace patient
4. Accès `/patient/rdv/prendre` → Sélection médecin, date, heure
5. Confirmation RDV → Email envoyé automatiquement
6. Consultation sur `/patient/consultations` et `/patient/ordonnances`

### Médecin — Consultation avec diagnostic IA
1. Connexion → Dashboard médecin
2. Navigation `/medecin/patients` → Sélection d'un patient
3. Consultation du dossier patient (infos, historique, RDV)
4. Création consultation : saisie symptômes par tags
5. Clic "Analyser avec l'IA" → Affichage Top 3 pathologies avec scores
6. Complétion du diagnostic manuel
7. Sauvegarde → Création ordonnance avec liste de médicaments
8. Génération PDF ordonnance et compte rendu

### Secrétaire — Gestion des rendez-vous
1. Connexion → Dashboard secrétaire
2. Navigation `/secretaire/rdv/nouveau`
3. Sélection patient, médecin, date, heure, type (présentiel / vidéo)
4. Choix statut (PLANIFIE / CONFIRME)
5. Sauvegarde → Lien Jitsi généré automatiquement si vidéo
6. Email de confirmation envoyé au patient
7. Suivi via calendrier ou liste

### Téléconsultation vidéo
1. Secrétaire crée un RDV de type EN_LIGNE → Lien UUID généré
2. Médecin et patient accèdent à `/consultation/{lien_visio}`
3. Jitsi Meet s'ouvre en plein écran
4. Le médecin utilise le panneau latéral pour rédiger la consultation
5. Le médecin peut lancer l'analyse IA pendant la vidéo
6. Fin de consultation → Statut RDV → TERMINE
7. Webhook n8n déclenché → Email "ordonnance disponible" envoyé au patient

---

*Généré le 2026-05-09 — MedPredict v2*
