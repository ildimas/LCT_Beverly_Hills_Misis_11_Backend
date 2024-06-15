FROM ubuntu:20.04
FROM python:3.10.2-slim
ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -y \
    && apt-get install -y python3-pip \
    && apt-get install -y libmagic-dev

WORKDIR /API

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .
