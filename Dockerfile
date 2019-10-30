FROM ubuntu:latest

WORKDIR /code

COPY . /code

# Download ubuntu packages
RUN apt-get update && apt-get install -y \
    git \
    # Needed for pg_config required to install psycopg2 (for SQLAlchemy)
    libpq-dev \
    python3.7 \
    python3-pip

# Enables native CLI
ENV PYTHONPATH=":/code"

RUN python3 setup.py install && \
    pip3 install -r requirements.txt
