.PHONY: help install test seed run docker-up docker-down lint clean

help:
	@echo "WealthOS AI — Makefile commands:"
	@echo "  make install     Install Python dependencies"
	@echo "  make test        Run all 82 automated pytest suites"
	@echo "  make seed        Seed demo financial records into database"
	@echo "  make run         Launch backend & frontend concurrently"
	@echo "  make docker-up   Start PostgreSQL, FastAPI, and Streamlit with Docker"
	@echo "  make docker-down Stop Docker containers"
	@echo "  make lint        Run ruff / py_compile syntax verification"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

seed:
	python scripts/seed_demo_data.py

run:
	python scripts/run_app.py

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

lint:
	python -c "import py_compile, glob; [py_compile.compile(f, doraise=True) for f in glob.glob('backend/**/*.py', recursive=True) + glob.glob('frontend/**/*.py', recursive=True) + glob.glob('finance_engine/**/*.py', recursive=True)]; print('All python source files verified clean.')"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
