FROM python:3.9-slim

WORKDIR /app

COPY user.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5004

CMD [ "python", "user.py" ]