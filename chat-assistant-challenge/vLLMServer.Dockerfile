FROM public.ecr.aws/docker/library/python:3.11
ENV PYTHONUNBUFFERED=1

RUN pip install vllm
COPY template.jinja /template.jinja
