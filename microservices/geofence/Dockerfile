FROM python:3.9-slim

WORKDIR /app

COPY geofence_server.py .
COPY geofence_pb2.py .
COPY geofence_pb2_grpc.py .
COPY invokes.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50051

CMD ["python", "geofence_server.py"]