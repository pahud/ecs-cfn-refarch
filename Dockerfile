FROM abiosoft/caddy:php

# Install dependencies

ENV ROOT_DIR /srv

RUN rm -rf $ROOT_DIR/*
ADD src $ROOT_DIR

EXPOSE 80
