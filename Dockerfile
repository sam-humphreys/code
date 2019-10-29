FROM ubuntu:latest

WORKDIR /code

COPY . /code

# Enables native CLI
ENV PYTHONPATH :/code

# Download ubuntu packages
RUN apt-get update && apt-get install -y \
    git \
    # Needed for pg_config required to install psycopg2 (for SQLAlchemy)
    libpq-dev \
    python3.7 \
    python3-pip

# Install 'code' as a package
RUN python3.7 setup.py install

# Install remaining packages
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt