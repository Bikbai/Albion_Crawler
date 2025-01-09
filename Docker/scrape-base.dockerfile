FROM python:3.12-slim-bookworm
ENV DOCKER_ENV="SCRAPER"
RUN mkdir /code
COPY requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt --root-user-action=ignore