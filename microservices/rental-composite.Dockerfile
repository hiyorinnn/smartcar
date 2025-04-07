FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rental-composite.py .
COPY requirements.txt .

ENV PYTHONUNBUFFERED=1
ENV PORT=5007
ENV CAR_AVAILABILITY_SERVICE_URL=http://car_available:5000
ENV BOOKING_LOG_SERVICE_URL=http://booking_log:5006/api


EXPOSE 5007

CMD ["python", "rental-composite.py"]