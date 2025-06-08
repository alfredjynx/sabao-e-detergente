# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    libopencv-dev \
    libatlas-base-dev \
    libhdf5-dev \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-h5py \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the model files into the container
COPY modelFiles/ /root/.deepface/weights/

# Baixar facenet.h5 diretamente do repositório oficial DeepFace
RUN mkdir -p /root/.deepface/weights/ \
 && curl -L -o /root/.deepface/weights/facenet.h5 https://github.com/serengil/deepface_models/releases/download/v1.0/facenet.h5

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install faiss-cpu 

COPY . /app/
