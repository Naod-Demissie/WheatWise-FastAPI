# FROM python:3.10

# WORKDIR /app

# COPY ./requirements.txt requirements.txt

# # RUN pip install torch==2.2.2

# RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

# COPY . .

# CMD ["fastapi", "run", "app/main.py", "--port", "8001"]


FROM nvcr.io/nvidia/pytorch:24.01-py3

FROM docker.io/nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables for CUDA
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility


WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt
# RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["fastapi", "run", "app/main.py", "--port", "8001"]