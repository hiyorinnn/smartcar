FROM python:3.9-slim

WORKDIR /app

COPY amqp_setup.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5010

CMD [ "python", "amqp_setup.py" ]