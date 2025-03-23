FROM public.ecr.aws/docker/library/python:3.11
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./mock_humanity_server/requirements.txt /code/mock_humanity_server/requirements.txt
RUN pip install -r /code/mock_humanity_server/requirements.txt

COPY ./mock_humanity_server /code/mock_humanity_server

COPY ./api-humanity-mock.py /code/api-humanity-mock.py

