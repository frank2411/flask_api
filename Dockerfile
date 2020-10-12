FROM python:3.6

COPY . app/
WORKDIR "/app"
RUN pip3 install -r requirements.txt

RUN touch .env
RUN echo "DB_ENGINE='postgresql+psycopg2'" > .env
RUN echo "DB_USER=postgres" > .env
RUN echo "DB_PASSWORD=admin" > .env
RUN echo "DB_HOST=localhost" > .env
RUN echo "DB_PORT=5432" > .env
RUN echo "DB_NAME=worklife" > .env

EXPOSE 8090

CMD flask run --host 0.0.0.0 -p 8090
