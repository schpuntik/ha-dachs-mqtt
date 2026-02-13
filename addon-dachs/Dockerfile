ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:13.2.1
FROM ${BUILD_FROM}

# Устанавливаем зависимости
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-requests \
    py3-paho-mqtt

# Копируем код аддона
COPY addon-dachs/dachs_mqtt  /usr/src/app/dachs_mqtt

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Устанавливаем зависимости Python (если есть requirements.txt)
# RUN pip install -r requirements.txt

# Команда запуска (без s6!)
CMD ["python3", "-m", "dachs_mqtt.dachs"]
