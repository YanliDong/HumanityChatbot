FROM public.ecr.aws/docker/library/python:3.11
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./api/requirements.txt /code/api/requirements.txt
RUN pip install -r /code/api/requirements.txt

RUN apt-get update && apt-get install nodejs npm -y

COPY ./api /code/api
WORKDIR /code/api/UI
RUN npm install
RUN npx webpack --config webpack.production.config.js

COPY ./api-app.py /code/api-app.py



