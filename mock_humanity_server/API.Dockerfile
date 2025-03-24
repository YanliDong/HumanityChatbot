FROM public.ecr.aws/docker/library/python:3.12-slim
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ./mock_humanity_server/requirements.txt /code/mock_humanity_server/requirements.txt
RUN pip install --no-cache-dir -r /code/mock_humanity_server/requirements.txt

COPY ./mock_humanity_server /code/mock_humanity_server
COPY ./api-humanity-mock.py /code/api-humanity-mock.py

# Add the mock_humanity_server directory to Python path
ENV PYTHONPATH=/code

CMD ["python3", "/code/api-humanity-mock.py"]

