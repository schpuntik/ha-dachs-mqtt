FROM python:3.11-slim

WORKDIR /app

COPY dachs.py /app/dachs.py
COPY run.sh /app/run.sh

RUN pip install requests paho-mqtt

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
