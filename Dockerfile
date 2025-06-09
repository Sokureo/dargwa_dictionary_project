FROM python:3.10.10-slim-bullseye

RUN apt update && apt upgrade -y
RUN apt install -y libmariadb-dev python-dev build-essential

WORKDIR /dargwa
COPY requirements.txt .

RUN pip3 install -r requirements.txt
RUN rm requirements.txt
