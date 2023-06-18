FROM python:3.9-slim

WORKDIR /worker

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /worker

EXPOSE 9876