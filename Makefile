SERVICES := api app
# Solo opera sobre los servicios que existan
EXISTING := $(foreach s,$(SERVICES),$(if $(wildcard $(s)/pyproject.toml),$(s)))

.PHONY: lint typecheck test build up down
lint:
	@for s in $(EXISTING); do (cd $$s && uv run ruff check . && uv run ruff format --check .) || exit 1; done
typecheck:
	@for s in $(EXISTING); do (cd $$s && uv run mypy src tests) || exit 1; done
test:
	@for s in $(EXISTING); do (cd $$s && uv run pytest) || exit 1; done
build:
	docker compose build
up:
	docker compose up --build -d
down:
	docker compose down
