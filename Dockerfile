# FROM python:3.10

# WORKDIR /app

# COPY ./requirements.txt requirements.txt

# # RUN pip install torch==2.2.2

# RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

# COPY . .

# CMD ["fastapi", "run", "app/main.py", "--port", "8001"]



FROM docker.io/nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility


RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["fastapi", "run", "app/main.py", "--port", "8001"]