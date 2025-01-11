FROM abome40k/albion-scraper:base
COPY ./*.py /code/
WORKDIR /code/
ENV DOCKER_ENV="SCRAPER"
ENV LOGGING.LEVEL="INFO"