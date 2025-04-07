FROM python:3.9-slim

WORKDIR /app

COPY notification.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5009

CMD [ "python", "notification.py" ]
