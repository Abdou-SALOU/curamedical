# ─────────────────────────────────────────────────────────────
#  MedPredict — Makefile
#  Usage : make <commande>
# ─────────────────────────────────────────────────────────────

.PHONY: help up down build restart logs shell-backend migrate seed \
        frontend-install ia train-ia clean prune status

## Affiche l'aide
help:
	@echo ""
	@echo "  MedPredict — Commandes disponibles"
	@echo "  ─────────────────────────────────────────────────"
	@echo "  make up            → Démarrer tous les services (db + backend + frontend)"
	@echo "  make down          → Arrêter et supprimer les conteneurs"
	@echo "  make build         → Rebuilder les images (cache préservé)"
	@echo "  make rebuild       → Rebuild FORCÉ sans cache (tout recommencer)"
	@echo "  make restart       → Redémarrer tous les services"
	@echo "  make logs          → Voir les logs en temps réel"
	@echo "  make logs-backend  → Logs backend uniquement"
	@echo "  make status        → État des conteneurs"
	@echo "  make shell-backend → Shell dans le conteneur backend"
	@echo "  make migrate       → Appliquer les migrations Django"
	@echo "  make seed          → Peupler la DB avec des données de test"
	@echo "  make ia            → Démarrer le service IA en local (hors Docker)"
	@echo "  make train-ia      → Ré-entraîner le modèle IA en local"
	@echo "  make clean         → Supprimer conteneurs + volumes"
	@echo "  make prune         → Nettoyer tout Docker (images orphelines)"
	@echo ""
	@echo "  ⚠  Le service IA tourne en LOCAL (pas dans Docker)."
	@echo "     Lancer 'make ia' dans un terminal séparé avant 'make up'."
	@echo ""

## Démarrer tous les services (sans rebuild)
up:
	docker-compose up -d

## Arrêter les conteneurs (conserve les volumes)
down:
	docker-compose down

## Rebuilder les images en préservant le cache Docker
build:
	docker-compose build

## Redémarrer tous les services
restart:
	docker-compose restart

## Rebuild forcé sans cache (pip install + npm install + entraînement IA from scratch)
rebuild:
	docker-compose build --no-cache
	docker-compose up -d

## Logs de tous les services en temps réel
logs:
	docker-compose logs -f

## Logs backend uniquement
logs-backend:
	docker-compose logs -f backend

## Logs frontend uniquement
logs-frontend:
	docker-compose logs -f frontend

## État des conteneurs
status:
	docker-compose ps

## Ouvrir un shell dans le conteneur backend
shell-backend:
	docker-compose exec backend sh

## Appliquer les migrations Django manuellement
migrate:
	docker-compose exec backend python manage.py migrate

## Créer un superutilisateur Django
createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

## Peupler la DB avec des données de test
seed:
	docker-compose exec backend python seed_users.py

## Démarrer le service IA en local (port 5000)
ia:
	cd ia-service && python app.py

## Ré-entraîner le modèle IA en local (utile après changement du dataset)
train-ia:
	cd ia-service && python train.py

## Supprimer conteneurs ET volumes (⚠ efface la DB et node_modules)
clean:
	docker-compose down -v

## Nettoyer les images Docker non utilisées
prune:
	docker image prune -f
	docker volume prune -f

## Afficher les variables d'environnement du backend
env:
	docker-compose exec backend env | sort
