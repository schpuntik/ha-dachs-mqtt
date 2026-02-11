ARG BUILD_FROM=ghcr.io/home-assistant/{arch}-base-python:3.11
FROM $BUILD_FROM

WORKDIR /app

COPY dachs.py /app/dachs.py
COPY run.sh /app/run.sh

RUN pip install --no-cache-dir requests paho-mqtt

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
