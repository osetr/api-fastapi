FROM ubuntu

RUN apt update; yes Yes | apt install python3-pip;

COPY . ./app

WORKDIR /app/

RUN /bin/bash -c "pip3 install -r requirements/requirements.txt"
