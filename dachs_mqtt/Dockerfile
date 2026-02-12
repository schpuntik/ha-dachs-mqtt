ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY dachs_mqtt/ ./dachs_mqtt/
COPY run.sh /run.sh

RUN chmod a+x /run.sh

# Устанавливаем Python, если его нет в образе
RUN if ! command -v python3 >/dev/null 2>&1; then \
        apk add --no-cache python3 py3-pip; \
    fi

RUN pip3 install --no-cache-dir --break-system-packages -r dachs_mqtt/requirements.txt


CMD [ "/run.sh" ]
