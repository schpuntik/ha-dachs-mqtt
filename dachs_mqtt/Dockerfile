ARG BUILD_FROM=ghcr.io/hassio-addons/base:15.0.5
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY dachs_mqtt/ ./dachs_mqtt/
COPY run.sh /run.sh

RUN chmod a+x /run.sh \
    && apk add --no-cache python3 py3-pip tzdata \
    && pip3 install --no-cache-dir -r dachs_mqtt/requirements.txt

CMD ["/run.sh"]
