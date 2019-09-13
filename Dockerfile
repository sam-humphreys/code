FROM python:3.6-slim

WORKDIR /code

COPY . /code

RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Enables executable CLI using 'coderun CMD ARGS'
ENV PYTHONPATH :/code