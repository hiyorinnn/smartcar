FROM python:3.9-slim

WORKDIR /app

COPY car_available.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "python", "car_available.py" ]
