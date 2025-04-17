FROM python:3.10-slim

WORKDIR /app

COPY ./requirements-docker.txt /app/requirements.txt

RUN apt-get update \
&& apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1

RUN pip install -r /app/requirements.txt \
&& rm -rf /root/.cache/pip

COPY . /app/