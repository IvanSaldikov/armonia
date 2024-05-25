ifneq ($(wildcard docker-compose.override.yml),)
	export COMPOSE_FILE := docker-compose.override.yml
endif

b:
	docker compose up --build -d
mig:
	docker compose exec backend python manage.py migrate --no-input
migs:
	docker compose exec --user root backend python manage.py makemigrations
migempty:
    # example of usage: `make app_name=ai_models empty_migration`
	docker-compose exec backend python manage.py makemigrations $(app_name) --empty
coll:
	docker compose exec --user root backend python manage.py collectstatic --no-input --clear
csup:
	docker-compose exec backend python manage.py createsuperuser
startapp:
    # example of usage: `make app_name=ai_models startapp`
	docker-compose exec backend python manage.py startapp $(app_name)
t:
	docker compose exec backend python manage.py test
test_coverage:
	docker compose exec backend python -m coverage run --source='.' manage.py test
coverage_report:
	docker compose exec backend python -m coverage html
lint:
	flake8
clean_container:
	docker container prune
clean_image:
	docker image prune
pre_commit_run:
	pre-commit run --all-files
