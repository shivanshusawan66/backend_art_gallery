target: | build-postgres build-redis build-workflow_application build-flower

build-postgres:
	docker compose -f ./ai_mf_dockerfiles/docker-compose.postgres.yml --env-file ./ai_mf_backend/.env up --build -d
build-redis:
	docker compose -f ./ai_mf_dockerfiles/docker-compose.redis.yml --env-file ./ai_mf_backend/.env up --build -d
build-workflow_application:
	docker compose -f ./ai_mf_dockerfiles/docker-compose.ai_mf_backend.yml --env-file ./ai_mf_backend/.env up --build -d
build-flower:
	docker compose -f ./ai_mf_dockerfiles/docker-compose.flower.yml --env-file ./ai_mf_backend/.env up --build -d
