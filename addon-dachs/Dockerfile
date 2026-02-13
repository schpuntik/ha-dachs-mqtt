ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app


COPY addon-dachs/dachs_mqtt/ ./dachs_mqtt/
COPY addon-dachs/run.sh /run.sh
COPY addon-dachs/service/run /etc/services.d/dachs/run

RUN chmod +x /run.sh \
    && chmod +x /etc/services.d/dachs/run \
    && if ! command -v python3 >/dev/null 2>&1; then \
         apk add --no-cache python3 py3-pip; \
       fi \
    && pip3 install --no-cache-dir --break-system-packages -r dachs_mqtt/requirements.txt
