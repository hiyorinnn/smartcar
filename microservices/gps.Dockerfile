FROM python:3.9-slim

WORKDIR /app

COPY gps.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5002

CMD [ "python", "gps.py" ]