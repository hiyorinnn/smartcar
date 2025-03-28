FROM python:3.9-slim

WORKDIR /app

COPY location.py .
COPY requirements.txt .
COPY invokes.py .
# Create a geofence directory and copy files there
RUN mkdir -p /app/geofence
COPY ./geofence/geofence_pb2.py /app/geofence/
COPY ./geofence/geofence_pb2_grpc.py /app/geofence/
COPY ./geofence/invokes.py /app/geofence/
# Create an init.py to make it a proper package
RUN touch /app/geofence/init.py

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD [ "python", "location.py" ]