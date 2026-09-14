FROM node:24-bookworm-slim AS frontend

WORKDIR /app/theme/static_src
COPY theme/static_src/package.json theme/static_src/package-lock.json ./
RUN npm ci
COPY theme/static_src/ ./
RUN mkdir -p /app/static/js
RUN npm run build


FROM python:3.14-slim-trixie AS application

RUN pip install --no-cache-dir uv==0.12.6

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/venv

WORKDIR /app

# Install the locked production environment before copying application code so
# dependency layers remain cached when only source files change.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . ./
COPY --from=frontend /app/theme/static/css/dist/ ./theme/static/css/dist/
COPY --from=frontend /app/static/js/alpine.min.js ./static/js/alpine.min.js

RUN uv run --no-sync python manage.py collectstatic --no-input

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health/', timeout=4).status == 200 else 1)"

CMD ["uv", "run", "--no-sync", "python", "manage.py", "runserver", "0.0.0.0:8000"]
