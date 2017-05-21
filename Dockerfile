#FROM abiosoft/caddy:php
FROM pahud/caddy

ENV ROOT_DIR /srv

RUN rm -rf $ROOT_DIR/*
ADD src $ROOT_DIR

EXPOSE 2015

