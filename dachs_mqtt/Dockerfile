ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

# Устанавливаем Python и pip (Debian-based)
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY dachs.py /app/dachs.py
COPY run.sh /app/run.sh

RUN pip3 install --no-cache-dir requests paho-mqtt

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
