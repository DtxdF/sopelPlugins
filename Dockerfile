FROM python:3-alpine

LABEL MAINTAINER="DtxdF@protonmail.com"
RUN apk add gcc build-base
RUN addgroup -S sopel && adduser -S sopel -G sopel
WORKDIR /home/sopel/.sopel/modules
RUN mkdir /home/sopel/.sopel/data
RUN chown -R sopel:sopel /home/sopel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY modules .

COPY config/default.cfg /home/sopel/.sopel/default.cfg

COPY data/welcome_messages /home/virgilio/.local/etc/virgilio/welcome_messages

RUN ls /home/sopel/.sopel


USER sopel
CMD ["sopel"]
