FROM python:3-alpine

LABEL MAINTAINER="DtxdF@protonmail.com"
RUN apk add gcc build-base
RUN addgroup -S sopel && adduser -S sopel -G sopel
WORKDIR /app

COPY --chown=sopel:sopel requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY --chown=sopel:sopel . .

USER sopel
CMD ["sopel"]
