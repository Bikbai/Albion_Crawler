FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install --yes curl git wget unzip
RUN mkdir /code
COPY requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt --root-user-action=ignore