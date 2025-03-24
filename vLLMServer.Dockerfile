FROM public.ecr.aws/docker/library/python:3.12-slim
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir transformers torch sentencepiece fastapi uvicorn jinja2
COPY template.jinja /template.jinja
COPY llm_server.py /llm_server.py

# Set environment variables for vLLM
ENV CUDA_VISIBLE_DEVICES=0
ENV VLLM_USE_CUDA=0

CMD ["python3", "/llm_server.py"]
