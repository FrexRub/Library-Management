FROM python:3.11

RUN mkdir /app && mkdir /app/src && mkdir /app/docker && mkdir /app/alembic
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y dist-upgrade
RUN apt install netcat-traditional
RUN pip install --upgrade pip "poetry==1.8.4"

RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY alembic.ini /app
COPY docker /app/docker
COPY alembic /app/alembic
COPY src /app/src

RUN chmod a+x docker/*.sh     # разрешение на запуск скриптов из каталога docker
