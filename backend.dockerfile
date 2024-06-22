FROM python:3.10

RUN mkdir backend

WORKDIR /backend

COPY . .

RUN pip install alembic
RUN pip install poetry
ENV PORT=8000
RUN poetry config virtualenvs.create false

RUN poetry install

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

ENV POSTGRES_HOST=pg_db
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=furys_db
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

##RUN sleep 15 && alembic upgrade head
#CMD ["alembic", "revision", "--autogenerate"]
#
#CMD ["alembic", "upgrade", "head"]
## Запуск приложения
#CMD ["python3", "main.py"]
