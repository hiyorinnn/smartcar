import sys
import os
from flask_cors import CORS
from flask import Flask, jsonify, request
import grpc

# Add the 'microservices' directory to the sys.path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'geofence'))

# Now import grpc server stuffs 
from geofence import geofence_pb2
from geofence import geofence_pb2_grpc

from invokes import invoke_http

app = Flask(__name__)
CORS(app)

#order_URL = "http://127.0.0.1:5002/api/ip_location" # Change to URL to use with docker
order_URL = "http://gps:5002/api/ip_location"

@app.route('/get_cars_by_location', methods=['GET'])
def get_cars_in_geofence():
    """
    Flask route that acts as a gRPC client.
    Uncomment code bellow to POST latitude and longitude for testing

    Sample data: 
    {
    "latitude": 1.375,
    "longitude": 103.84
    }

    # data = request.get_json()
    # user_latitude = data.get('latitude')
    # user_longitude = data.get('longitude')

    # if user_latitude is None or user_longitude is None:
    #     return jsonify({'error': 'Latitude and longitude are required'}), 400

    """
    
    try:
        # Invoke the gps microservice
        user_latitude, user_longitude = get_gps()

        with grpc.insecure_channel('geofence:50051') as channel: #update to work with docker
            stub = geofence_pb2_grpc.GeofenceServiceStub(channel)
            request_grpc = geofence_pb2.GeofenceRequest(user_latitude=user_latitude, user_longitude=user_longitude)
            response_grpc = stub.GetCarsInGeofence(request_grpc)

            cars = []
            for car in response_grpc.cars:
                cars.append({
                    'id': car.id,
                    'make': car.make,
                    'model': car.model,
                    'year': car.year,
                    'color': car.color,
                    'price_per_hour': car.price_per_hour,
                    'available': car.available,
                    'latitude': car.latitude,
                    'longitude': car.longitude,
                    'location' : car.town
                })
            print(f"return total of: {len(cars)} cars")

            return jsonify({'cars': cars})

    except grpc.RpcError as e:
        return jsonify({'error': str(e.details())}), 500

def get_gps():
# Invoke the gps microservice
    print("  Invoking gps microservice...")
    gps_result = invoke_http(
        order_URL, method="GET"
    )
    # print(f"  gps_result:{gps_result['latitude'], gps_result['longitude']}\n")
    return gps_result["latitude"], gps_result["longitude"]


@app.route('/get_cars_by_location/<location>', methods=['GET'])
def get_cars_by_location(location):
    try:
        with grpc.insecure_channel('geofence:50051') as channel:
            stub = geofence_pb2_grpc.GeofenceServiceStub(channel)
            request_grpc = geofence_pb2.GeofenceRequest(location=location)
            response_grpc = stub.GetCarsInLocation(request_grpc)

            cars = []
            for car in response_grpc.cars:
                cars.append({
                    'id': car.id,
                    'make': car.make,
                    'model': car.model,
                    'year': car.year,
                    'color': car.color,
                    'price_per_hour': car.price_per_hour,
                    'available': car.available,
                    'latitude': car.latitude,
                    'longitude': car.longitude,
                    'town':car.town
                })
            print(f"return total of: {len(cars)} cars")
            return jsonify({'cars': cars})

    except grpc.RpcError as e:
        return jsonify({'error': str(e.details())}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)