FROM python:3-alpine

LABEL MAINTAINER="DtxdF@protonmail.com"
RUN apk add gcc build-base
RUN addgroup -S sopel && adduser -S sopel -G sopel
WORKDIR /home/sopel/.sopel/modules
RUN chown -R sopel:sopel /home/sopel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

USER sopel
CMD ["sopel"]
