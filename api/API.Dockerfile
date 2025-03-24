FROM node:18 as ui-builder

WORKDIR /ui
COPY ./api/UI /ui
RUN npm cache clean --force
RUN rm -rf node_modules package-lock.json
RUN npm install --legacy-peer-deps
RUN npm install --save-dev @babel/core @babel/preset-env @babel/preset-react babel-loader webpack webpack-cli @babel/plugin-transform-runtime @babel/runtime
ENV NODE_ENV=production
RUN ./node_modules/.bin/webpack --config webpack.production.config.js

FROM public.ecr.aws/docker/library/python:3.12-slim
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /code

# Install Node.js 18.x
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY ./api/requirements.txt /code/api/requirements.txt
RUN pip install --no-cache-dir -r /code/api/requirements.txt

# Copy the entire api directory
COPY ./api /code/api

# Copy the built UI files
COPY --from=ui-builder /ui/static/build /code/api/UI/static/build
COPY --from=ui-builder /ui/home.html /code/api/UI/home.html

# Copy the main application file
COPY ./api-app.py /code/api-app.py

# Set up Python path to include the api directory
ENV PYTHONPATH=/code:/code/api

# Create necessary directories
RUN mkdir -p /code/api/logs/client

CMD ["python3", "/code/api-app.py"]



