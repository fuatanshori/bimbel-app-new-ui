FROM python:3.10.14-slim-bullseye

WORKDIR /app

COPY . .

RUN apt-get update && apt upgrade -y\
&& apt-get install python3-dev -y\
&& apt-get install default-libmysqlclient-dev -y\
&& apt-get install build-essential -y\
&& apt install pkg-config -y\
&& pip install -r requirements.txt\
&& apt-get install curl -y