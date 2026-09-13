FROM python:3.12-slim

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/local.txt

COPY app/ app/
COPY config/ config/
COPY tests/ tests/
COPY alembic/ alembic/
COPY alembic.ini pyproject.toml ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
