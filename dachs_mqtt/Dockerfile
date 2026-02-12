ARG BUILD_FROM=ghcr.io/home-assistant/{arch}-base-python:3.12
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY dachs_mqtt/ ./dachs_mqtt/
COPY run.sh /run.sh

RUN chmod a+x /run.sh \
    && pip3 install --no-cache-dir -r dachs_mqtt/requirements.txt

CMD [ "/run.sh" ]
