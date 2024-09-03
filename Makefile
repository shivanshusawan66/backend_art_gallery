target: | build-mongo build-redis build-workflow_application build-flower

build-mongo:
	docker compose -f ./dockerfiles/docker-compose.mongo.yml --env-file ./ai_mf_backend/.env up --build -d
build-redis:
	docker compose -f ./dockerfiles/docker-compose.redis.yml --env-file ./ai_mf_backend/.env up --build -d
build-workflow_application:
	docker compose -f ./dockerfiles/docker-compose.ai_mf_backend.yml --env-file ./ai_mf_backend/.env up --build -d
build-flower:
	docker compose -f ./dockerfiles/docker-compose.flower.yml --env-file ./ai_mf_backend/.env up --build -d
