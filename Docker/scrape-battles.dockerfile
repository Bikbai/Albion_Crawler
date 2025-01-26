FROM abome40k/albion-scraper:base
ARG VERSION
COPY ./*.py /code/
RUN echo $VERSION > /code/version.txt
WORKDIR /code/
ENV DOCKER_ENV="SCRAPER"
ENV LOGGING.LEVEL="INFO"