############################
# STAGE 1: Builder stage

FROM python:3.12.9-slim AS builder

# as stated in F6
ENV MODEL_SERVICE_PORT=8081

WORKDIR /app

# install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY . .

############################
# STAGE 2: Runtime stage

FROM python:3.12.9-slim 

ENV MODEL_SERVICE_PORT=8081

WORKDIR /app

COPY --from=builder /install /usr/local

COPY --from=builder /app /app

RUN mkdir -p output

EXPOSE ${MODEL_SERVICE_PORT}

CMD ["python", "src/serve_model.py"]