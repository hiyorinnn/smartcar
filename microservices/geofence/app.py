from flask import Flask, jsonify, request
import grpc
import geofence_pb2
import geofence_pb2_grpc

app = Flask(__name__)

@app.route('/get_cars_in_geofence', methods=['POST'])
def get_cars_in_geofence():
    """
    Flask route that acts as a gRPC client.
    """
    data = request.get_json()
    user_latitude = data.get('latitude')
    user_longitude = data.get('longitude')

    if user_latitude is None or user_longitude is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    try:
        with grpc.insecure_channel('localhost:50051') as channel:
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
                })

            return jsonify({'cars': cars})

    except grpc.RpcError as e:
        return jsonify({'error': str(e.details())}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)