FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install --yes python3
RUN apt-get install --yes python3-dev
RUN apt-get install --yes nginx
RUN apt-get install --yes python3-pip
RUN apt-get install --yes virtualenv
RUN mkdir /src
COPY . /src

WORKDIR /src

RUN virtualenv -p /usr/bin/python3 env
RUN . env/bin/activate
RUN pip3 install -r requirements.pip
RUN cp /src/nginx.conf /etc/nginx/
RUN /etc/init.d/nginx start

EXPOSE 80
EXPOSE 8000
