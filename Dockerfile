FROM python:3.6-slim

WORKDIR /code

COPY . /code

# Enables native CLI
ENV PYTHONPATH :/code

RUN python setup.py install

RUN pip install --trusted-host pypi.python.org -r requirements.txt