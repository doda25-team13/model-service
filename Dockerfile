FROM python:3.12.9-slim AS base

############################
# STAGE 1: Builder stage

FROM base AS builder

# as stated in F6
ENV MODEL_SERVICE_PORT=8081

WORKDIR /app

# install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

############################
# STAGE 2: Runtime stage

FROM base

ENV MODEL_SERVICE_PORT=8081
ENV MODEL_DIR=/models
ENV MODEL_VERSION=latest
ENV MODEL_REPO=doda25-team13/model-service
    
WORKDIR /app

COPY --from=builder /install /usr/local

COPY src/ ./src/

RUN mkdir -p /models

EXPOSE ${MODEL_SERVICE_PORT}

CMD ["python", "src/serve_model.py"]