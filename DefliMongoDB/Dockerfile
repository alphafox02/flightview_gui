FROM python:3.9

WORKDIR /app

COPY restart_script.py /app/restart_script.py
COPY adsb-data-collector.py /app/adsb-data-collector.py
COPY config.py /app/config.py

RUN pip install aiohttp motor pymongo python-dateutil

CMD ["python", "restart_script.py"]
