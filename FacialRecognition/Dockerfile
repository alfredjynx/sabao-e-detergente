# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    libopencv-dev \
    libatlas-base-dev \
    libhdf5-dev \
    python3-h5py \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

    
    
# Set the working directory inside the container
WORKDIR /app

# Copy the model files into the container
COPY modelFiles/ /root/.deepface/weights/

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install faiss-cpu 

COPY . /app/
