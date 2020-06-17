FROM ubuntu

RUN apt update; yes Yes | apt install python3-pip; yes Yes | pip3 install virtualenv;

COPY . ./app

WORKDIR /app/

RUN /bin/bash -c "virtualenv venv && source venv/bin/activate && pip3 install -r requirements.txt"
