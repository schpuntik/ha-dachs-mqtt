ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

# Устанавливаем Python и pip
RUN apk add --no-cache python3 py3-pip

COPY dachs.py /app/dachs.py
COPY run.sh /app/run.sh

RUN pip install --no-cache-dir requests paho-mqtt

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
