# Brief de complétion — MedPredict_Rapport.docx

> **Objectif :** Ce document liste toutes les corrections, ajouts et sections manquantes à intégrer dans le rapport MedPredict. Chaque point indique **où** intervenir, **ce qu'il faut écrire** et **les données techniques exactes** issues du code source.

---

## 0. Informations générales sur le projet (à avoir en tête)

| Élément | Valeur réelle |
|---------|--------------|
| Nom commercial | CuraMedical (affiché dans l'UI) / MedPredict (nom du projet) |
| Date du rapport | 23 Mars 2026 → à mettre à jour si nécessaire |
| Stack backend | Django REST Framework, Python, JWT (SimpleJWT), django-auditlog, ReportLab, PostgreSQL |
| Stack frontend | React 19, Vite 7, Tailwind CSS v4, Zustand, React Router v7, Recharts, Lucide React, @jitsi/react-sdk |
| Service IA | Flask + Scikit-Learn (Random Forest) — port **5005** |
| Automatisation | n8n (2 workflows) |
| Conteneurs | 4 services Docker Compose : frontend, backend, db, ia-service |
| Rôles utilisateurs | **4 rôles** : Administrateur, Médecin, Secrétaire, **Patient** |
| Authentification JWT | Access token : 8h — Refresh token : 7 jours — Rotation activée |

---

## 1. CORRECTIONS D'ERREURS (points factuellement faux)

### 1.1 Port du service IA
- **Où** : Section 3.1 et tableau Section 3.2
- **Erreur** : le rapport indique port `5000`
- **Correction** : le port réel est **`5005`**

### 1.2 Le patient n'est PAS un acteur passif
- **Où** : Section 4 — Diagramme de Cas d'Utilisation, description du rôle Patient
- **Erreur** : *« Son dossier est géré par les autres acteurs mais il n'interagit pas directement avec le système informatique. »*
- **Correction** : Le patient dispose d'un espace complet. Il peut :
  - S'auto-inscrire via `/register` (création automatique User + Patient)
  - Se connecter et accéder à son tableau de bord personnel
  - Consulter ses rendez-vous à venir et en créer de nouveaux
  - Visualiser ses consultations et les symptômes enregistrés
  - Télécharger ses ordonnances en PDF
  - Accéder à son profil médical (`/profile`) : informations civiles, allergies, antécédents
  - Participer à une téléconsultation vidéo via le lien Jitsi

### 1.3 Nombre de rôles : 3 mentionnés au lieu de 4
- **Où** : Section 3.3 (RBAC) et Section 4 (acteurs du Use Case)
- **Erreur** : Le rapport liste Administrateur, Médecin, Secrétaire — le rôle **Patient** est absent
- **Correction** : Ajouter le rôle Patient dans toutes les descriptions RBAC avec ses droits spécifiques :

| Ressource | Admin | Médecin | Secrétaire | Patient |
|-----------|-------|---------|------------|---------|
| Patients | CRUD complet | Lecture (ses patients) | CRUD | Lecture (son profil uniquement) |
| Rendez-vous | CRUD complet | Lecture (ses RDV) | CRUD complet | CRUD (ses RDV) |
| Consultations | Lecture | CRUD complet | Lecture | Lecture (siennes uniquement) |
| Ordonnances | Lecture | CRUD complet | Lecture | Lecture + téléchargement PDF |
| Utilisateurs | CRUD complet | — | — | — |
| Module IA | — | Oui | — | — |
| Téléconsultation | — | Panel médecin | — | Participant vidéo |

### 1.4 Cycle de statuts des rendez-vous incomplet
- **Où** : Section 2.2
- **Erreur** : Le rapport liste 4 statuts (`Planifié → Confirmé → En cours → Terminé`)
- **Correction** : Il y a **6 statuts** : `DEMANDE → PLANIFIE → CONFIRME → EN_COURS → TERMINE / ANNULE`

---

## 2. SECTIONS MANQUANTES — À AJOUTER INTÉGRALEMENT

### 2.1 MODULE ORDONNANCES (section 2.X manquante)

**Titre suggéré :** `2.5. Gestion des Ordonnances Médicales`

**Contenu à rédiger :**

Le module d'ordonnances permet au médecin de rédiger des prescriptions structurées directement depuis l'interface de consultation. Chaque ordonnance est liée en OneToOne à une consultation.

Fonctionnalités :
- **Liste dynamique de médicaments** : Chaque ordonnance peut contenir N lignes de prescription, chacune comportant : nom du médicament, dosage (ex : 500mg), unité (Comprimé / Gélule / Sachet / Ampoule / Sirop / Gouttes / Crème), fréquence (ex : 3x/jour), durée (ex : 7 jours), instructions spéciales (ex : à prendre pendant les repas)
- **Aperçu temps réel** : Un panneau de prévisualisation affiche le rendu final de l'ordonnance pendant la saisie, avant enregistrement
- **Génération PDF automatique** : Endpoint `GET /api/prescriptions/{id}/pdf/` génère un document PDF professionnel via ReportLab (en-tête cabinet, tableau médicaments, signature)
- **Accès patient** : Le patient peut télécharger ses ordonnances depuis son espace personnel
- **Recherche** : Par nom de patient, prénom, ou nom de médicament
- **Webhook n8n** : À la finalisation du rendez-vous (statut → TERMINE), un webhook déclenche l'envoi d'un email au patient l'informant que son ordonnance est disponible

### 2.2 TÉLÉCONSULTATION VIDÉO (section manquante)

**Titre suggéré :** `2.6. Module de Téléconsultation Vidéo`

**Contenu à rédiger :**

MedPredict intègre nativement un module de vidéoconférence médicale reposant sur **Jitsi Meet** (open source, sans serveur dédié requis) via le SDK `@jitsi/react-sdk`.

Fonctionnement :
1. La secrétaire ou l'admin crée un rendez-vous de type **EN_LIGNE** — un UUID de salle Jitsi est généré automatiquement côté backend et stocké dans le champ `teleconsultation_link`
2. Le médecin et le patient accèdent à la même salle via l'URL `https://meet.jit.si/{UUID}`
3. Côté médecin : un panneau latéral permet de rédiger la consultation (symptômes, diagnostic) **en temps réel pendant la vidéo**, sans quitter l'écran
4. Le module IA est accessible pendant la téléconsultation (bouton « Analyser avec l'IA »)
5. En fin de consultation, le médecin clique « Quitter » — le statut du RDV passe automatiquement à TERMINE, déclenchant le workflow n8n d'envoi d'ordonnance

Sécurité : l'accès à la salle est limité aux utilisateurs authentifiés (JWT vérifié avant affichage du lien de connexion).

### 2.3 ESPACE PATIENT (section manquante)

**Titre suggéré :** `2.7. Portail Patient`

**Contenu à rédiger :**

Contrairement aux solutions médicales traditionnelles où le patient est un objet passif du dossier, MedPredict leur offre un espace autonome et sécurisé.

**Auto-inscription** : Le patient peut créer son compte via `/register` — la requête crée simultanément un compte utilisateur (`User`) et un dossier patient (`Patient`) lié par relation `OneToOne`.

**Tableau de bord patient** : Après connexion, le patient accède à :
- Ses rendez-vous à venir avec statut en temps réel
- Ses consultations passées avec les symptômes enregistrés et le diagnostic posé
- Ses ordonnances téléchargeables en PDF à tout moment
- La prise de rendez-vous en ligne (choix du médecin, date, heure, type présentiel/vidéo)

**Page profil** (`/profile`) : Consultation de son dossier médical complet (informations civiles, groupe sanguin, allergies, antécédents, historique complet des consultations et ordonnances).

**Navigation adaptative** : La sidebar et la navigation mobile s'adaptent automatiquement au rôle patient — seules les sections pertinentes sont affichées.

### 2.4 NOTIFICATIONS ET AUTOMATISATION N8N (section manquante)

**Titre suggéré :** `2.8. Automatisation et Notifications (n8n)`

**Contenu à rédiger :**

MedPredict intègre **n8n** (plateforme d'automatisation de workflows) pour gérer l'ensemble des communications automatisées sans développement custom côté backend.

**Workflow 1 — Rappel 24h avant rendez-vous :**

| Étape | Action |
|-------|--------|
| 1. Schedule Trigger | Déclenché chaque matin à 8h00 |
| 2. Authentification | Récupère un token JWT via `POST /api/token/` |
| 3. Requête API | Appelle `GET /api/appointments/?date={demain}` pour récupérer les RDV du lendemain |
| 4. Itération | Parcourt chaque rendez-vous trouvé |
| 5. Email | Envoie un rappel personnalisé (nom du patient, médecin, heure, type présentiel/vidéo) |

**Workflow 2 — Ordonnance disponible (RDV terminé) :**

| Étape | Action |
|-------|--------|
| 1. Webhook | Reçoit un POST de Django (`post_save` signal, statut → TERMINE) |
| 2. Email | Envoie un email au patient : *« Votre ordonnance est disponible, connectez-vous pour la télécharger »* |

**Emails** : Templates HTML stylisés avec variables dynamiques (nom du patient, date, lien d'accès).

### 2.5 AUDIT ET TRAÇABILITÉ (section manquante)

**Titre suggéré :** À intégrer dans la Section 3.3 (Sécurité) ou créer `3.4. Audit et Traçabilité`

**Contenu à rédiger :**

MedPredict implémente un journal d'audit complet via la bibliothèque **django-auditlog**. Chaque modification sur les objets sensibles est enregistrée avec :
- L'utilisateur auteur de l'action
- Le type d'action (création / modification / suppression)
- L'horodatage précis
- L'objet modifié et les champs concernés

**Objets tracés** : `User`, `Patient`, `Consultation`, `Prescription`

L'administrateur dispose d'une vue dédiée dans l'interface pour consulter l'historique complet des modifications. Le middleware JWT garantit que chaque entrée de log est associée à un utilisateur authentifié identifié.

### 2.6 ARCHIVAGE (SOFT DELETE) (section manquante)

**À ajouter dans :** Section 2.1 (Gestion des Patients)

**Contenu à ajouter :**

La suppression d'un patient est **non destructive** (Soft Delete). Au lieu de supprimer définitivement, le système archive le dossier :
- Le patient est marqué `is_archived = True`
- Tous ses rendez-vous, consultations et ordonnances associés sont archivés en cascade
- Le dossier disparaît de la liste active et est déplacé dans la **Corbeille** (`/patients/trash`)
- L'administrateur peut **restaurer** le dossier complet (patient + données liées) en un clic via `POST /api/patients/{id}/restore/`
- Cette approche garantit la conformité RGPD et prévient les pertes accidentelles de données médicales

---

## 3. COMPLÉMENTS AUX SECTIONS EXISTANTES

### 3.1 Section 3.1 — Architecture : ajouter n8n comme 5ème composant

Ajouter dans le tableau des composants :

| Composant | Rôle |
|-----------|------|
| n8n (Automatisation) | Orchestration des workflows de notifications. S'authentifie auprès du backend Django via JWT et consomme l'API REST pour envoyer des rappels et des emails transactionnels aux patients. |

Mettre à jour la description : *« L'architecture de MedPredict adopte une approche orientée micro-services, segmentée en **cinq** briques autonomes... »*

### 3.2 Section 3.2 — Compléter la stack technique

Ajouter dans la description Frontend :

> Le frontend s'appuie sur un écosystème moderne : **Zustand** pour la gestion d'état globale (authentification, notifications), **Recharts** pour les visualisations statistiques du tableau de bord, **Lucide React** pour l'iconographie SVG vectorielle, et **@jitsi/react-sdk** pour l'intégration vidéo. Le design système est construit sur **Tailwind CSS v4** avec des tokens CSS personnalisés (`@theme`) et un thème dark mode premium.

### 3.3 Section 6 — IA : compléter le mapping des symptômes

**À ajouter dans 6.1 :**

> Le microservice implémente un mapping bidirectionnel Français → Anglais pour les 35 symptômes supportés (ex : `fièvre → Fever`, `toux → Cough`, `douleur thoracique → Chest Pain`), permettant une interface utilisateur entièrement en français tout en conservant les features du modèle entraîné en anglais. Les 3 prédictions retournées incluent : le nom de la pathologie, le score de confiance en pourcentage, et une phrase d'explication textuelle. Ces résultats sont stockés dans le champ `ia_suggestions` (JSONField) de la consultation et le flag `ia_used` (booléen) permet de calculer le taux d'adoption du module IA.

**Paramètres d'entrée du modèle :**
- Symptômes sélectionnés (tableau de valeurs)
- Âge du patient (récupéré automatiquement depuis le dossier)
- Genre (M/F, récupéré depuis le dossier)
- Pression artérielle (Basse / Normale / Haute)
- Niveau de cholestérol (Bas / Normal / Élevé)

### 3.4 Section 7 — Design System : mettre à jour la charte graphique

**Remplacer ou compléter le contenu de 7.1 :**

> La charte graphique de MedPredict a évolué vers un thème **Dark Premium SaaS** tout en conservant la signature médicale de l'Émeraude. Le fond global est un noir profond (`#060b18`) avec des halos de couleur en arrière-plan (dégradé émeraude en haut à gauche, indigo en haut à droite), évoquant un environnement de travail médical nocturne et concentré. Les cards et surfaces utilisent un **glassmorphisme sombre** (`rgba(12,18,35,0.75)` + `backdrop-filter: blur(28px)`), créant une hiérarchie visuelle par profondeur. Les badges de statut sont translucides (fond `rgba(couleur, 0.15)` + bordure `rgba(couleur, 0.25)`), lisibles sur fond sombre. Les boutons primaires conservent le gradient émeraude → teal avec un glow renforcé (`box-shadow: 0 8px 28px rgba(16,185,129,0.45)`).

### 3.5 Section 8 — Mettre à jour l'état des lieux

**Remplacer intégralement le contenu de 8.1 et 8.2 :**

**8.1 — Fonctionnalités terminées et opérationnelles :**

- ✅ Authentification JWT sécurisée (access 8h / refresh 7 jours / rotation activée)
- ✅ RBAC complet — 4 rôles : Administrateur, Médecin, Secrétaire, Patient
- ✅ CRUD complet des Patients avec archivage (Soft Delete) + corbeille + restauration
- ✅ Gestion des Rendez-vous (6 statuts, anti-conflit horaire, filtres par date/statut)
- ✅ Téléconsultation vidéo intégrée (Jitsi Meet, UUID auto-généré, panel médecin temps réel)
- ✅ Module Consultation avec saisie symptômes par tags (35 symptômes), examen clinique, diagnostic
- ✅ Module IA diagnostique (Random Forest, top 3 pathologies avec score de confiance)
- ✅ Génération PDF compte-rendu de consultation (ReportLab)
- ✅ Module Ordonnances avec lignes de médicaments dynamiques et aperçu temps réel
- ✅ Génération PDF ordonnance médicale (ReportLab)
- ✅ Portail patient complet (profil, RDV, consultations, ordonnances téléchargeables)
- ✅ Auto-inscription patient (`/register`)
- ✅ Tableau de bord analytique par rôle (KPIs, graphiques mensuels, top diagnostics, taux IA)
- ✅ Chatbot IA conversationnel (widget flottant, intégration n8n)
- ✅ Workflows n8n : rappel 24h avant RDV + notification ordonnance disponible
- ✅ Emails automatisés (confirmation RDV, rappels, notifications)
- ✅ Audit log complet (django-auditlog sur User, Patient, Consultation, Prescription)
- ✅ API REST auto-documentée (Swagger UI sur `/api/docs/`, OpenAPI JSON sur `/api/schema/`)
- ✅ Design système dark mode premium (thème cohérent, responsive mobile-first, bottom nav)
- ✅ Déploiement conteneurisé Docker Compose (5 services)

**8.2 — Perspectives d'évolution :**

- Intégration de notifications push navigateur (Web Push API)
- Application mobile native (React Native) pour les patients
- Module de statistiques avancées exportables (CSV/Excel)
- Prise en charge de plusieurs cabinets (multi-tenant)
- Intégration avec des dispositifs médicaux connectés (IoT)

---

## 4. SECTIONS ENTIÈREMENT NOUVELLES À CRÉER

### 4.1 Modèle de données (ERD)

**Titre :** `5.bis — Modèle Relationnel de la Base de Données`
**Placer entre** la section 5 (Classes) et la section 6 (IA)

**Contenu à rédiger + décrire le schéma ERD suivant :**

```
User ─────────────────── OneToOne ──────────── Patient
 │                                                │
 │ (FK doctor)                                    │ (FK patient)
 ↓                                                ↓
Appointment ──────────── FK ──────────────── Consultation
 (patient FK, doctor FK)                          │
                                          FK ─────┤
                                                   ↓
                                             Prescription
                                                   │
                                                   ↓
                                          PrescriptionItem (N lignes)
```

**Tables et champs principaux :**

| Table | Champs clés |
|-------|-------------|
| `User` | id, username, email, first_name, last_name, phone, role (admin/doctor/secretary/patient), is_active |
| `Patient` | id, first_name, last_name, date_of_birth, gender, national_id, phone, email, address, blood_group, allergies, medical_history, is_archived, user (FK OneToOne nullable) |
| `Appointment` | id, patient (FK), doctor (FK), scheduled_at, duration, reason, status (6 valeurs), is_teleconsultation, teleconsultation_link, is_archived |
| `Consultation` | id, appointment (FK), symptoms (JSONField), clinical_exam, diagnosis, notes, ia_suggestions (JSONField), ia_used (bool), is_archived, created_at |
| `Prescription` | id, consultation (FK OneToOne), notes, created_at, is_archived |
| `PrescriptionItem` | id, prescription (FK), medication, dosage, unit, frequency, duration, instructions |

### 4.2 Documentation API

**Titre :** `9.bis — Documentation de l'API REST`
**Placer avant ou après** la section Déploiement

**Contenu :**

L'API REST de MedPredict est entièrement auto-documentée via **drf-spectacular** :

- **Swagger UI interactif** : `GET /api/docs/` — Interface graphique permettant de tester tous les endpoints en temps réel
- **Schéma OpenAPI** : `GET /api/schema/` — Définition complète au format JSON

**Principaux groupes d'endpoints :**

| Groupe | Préfixe | Méthodes disponibles |
|--------|---------|---------------------|
| Authentification | `/api/token/` | POST (login), POST (refresh) |
| Utilisateurs | `/api/users/` | GET, POST, PUT, DELETE |
| Médecins actifs | `/api/users/doctors/` | GET |
| Patients | `/api/patients/` | GET, POST, PUT, DELETE |
| Corbeille patients | `/api/patients/trash/` | GET |
| Restauration | `/api/patients/{id}/restore/` | POST |
| Rendez-vous | `/api/appointments/` | GET, POST, PATCH, DELETE |
| Consultations | `/api/consultations/` | GET, POST, PATCH, DELETE |
| Suggestion IA | `/api/consultations/ia/suggest/` | POST |
| PDF consultation | `/api/consultations/{id}/compte-rendu-pdf/` | GET |
| Ordonnances | `/api/prescriptions/` | GET, POST, DELETE |
| PDF ordonnance | `/api/prescriptions/{id}/pdf/` | GET |
| Chatbot | `/api/chat/` | POST |

**Sécurité** : Tous les endpoints (sauf `/api/token/` et `/register/`) requièrent un header `Authorization: Bearer {access_token}`.

### 4.3 Conclusion

**Titre :** `10. Conclusion`

**Points à aborder :**
- MedPredict est un système complet de gestion médicale, passé d'un concept initial à une solution production-ready en un semestre
- L'architecture micro-services (Django + Flask + n8n) démontre la capacité à orchestrer des composants spécialisés
- L'intégration de l'IA diagnostique apporte une valeur ajoutée réelle, mesurable (taux d'adoption visible dans le dashboard)
- Le projet couvre l'intégralité du cycle de soin : de la prise de rendez-vous à l'ordonnance PDF, en passant par la consultation vidéo
- Compétences mobilisées : développement fullstack (Python/React), DevOps (Docker), Machine Learning (scikit-learn), conception UML, gestion de projet

### 4.4 Bibliographie

**Titre :** `Références`

Liste des technologies et ressources utilisées :
- Django REST Framework — https://www.django-rest-framework.org/
- SimpleJWT — https://django-rest-framework-simplejwt.readthedocs.io/
- django-auditlog — https://django-auditlog.readthedocs.io/
- ReportLab — https://www.reportlab.com/
- React — https://react.dev/
- Tailwind CSS — https://tailwindcss.com/
- Recharts — https://recharts.org/
- Jitsi Meet React SDK — https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-react-sdk/
- scikit-learn (Random Forest) — https://scikit-learn.org/
- n8n Workflow Automation — https://n8n.io/
- Docker Compose — https://docs.docker.com/compose/

---

## 5. CHECKLIST FINALE

```
Corrections d'erreurs :
☐ Corriger port IA : 5000 → 5005 (§3.1 et §3.2)
☐ Corriger rôle Patient : acteur actif, pas passif (§4)
☐ Ajouter rôle Patient dans le tableau RBAC (§3.3)
☐ Corriger cycle statuts RDV : 6 statuts, pas 4 (§2.2)

Compléments sections existantes :
☐ §2.1 — Ajouter archivage soft delete + corbeille + restauration
☐ §2.2 — Ajouter anti-conflit, téléconsultation, email, vue calendrier
☐ §3.1 — Ajouter n8n comme 5ème composant, corriger diagramme
☐ §3.2 — Compléter stack frontend (Zustand, Recharts, Jitsi SDK, Tailwind v4)
☐ §3.3 — Ajouter Patient au RBAC, compléter JWT (rotation, durées)
☐ §6.1 — Compléter mapping FR→EN symptômes, paramètres d'entrée, stockage JSON
☐ §7.1 — Mettre à jour charte graphique (dark mode premium SaaS)
☐ §8.1 — Réécrire liste des fonctionnalités terminées (toutes les vraies)
☐ §8.2 — Retirer ce qui est fait, réécrire les perspectives réelles

Nouvelles sections à créer :
☐ §2.5 — Module Ordonnances
☐ §2.6 — Téléconsultation Vidéo (Jitsi)
☐ §2.7 — Portail Patient
☐ §2.8 — Automatisation n8n + Notifications
☐ §3.4 — Audit & Traçabilité (django-auditlog)
☐ §5.bis — Modèle Relationnel / ERD
☐ §9.bis — Documentation API REST (Swagger)
☐ §10 — Conclusion
☐ Références / Bibliographie
```

---

*Document généré le 2026-05-09 — à utiliser comme brief pour la complétion du rapport MedPredict*
