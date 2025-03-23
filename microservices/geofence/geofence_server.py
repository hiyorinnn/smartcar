import grpc
import requests
import geofence_pb2
import geofence_pb2_grpc
from concurrent import futures

def is_within_geofence(user_lat, user_lon, car_lat, car_lon, radius=0.01): #Change radius to define the geofence
    # Simple distance calculation 
    return (user_lat - car_lat)**2 + (user_lon - car_lon)**2 <= radius**2

class GeofenceServicer(geofence_pb2_grpc.GeofenceServiceServicer):
    def GetCarsInGeofence(self, request, context):
        user_lat = request.user_latitude
        user_lon = request.user_longitude

        # Make an API call to car_avaliability microservice
        try:
            response = requests.get('http://127.0.0.1:5000/car/available')  # Replace with your Flask service's URL
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            car_data = response.json()

            if car_data['code'] != 200:
                context.abort(grpc.StatusCode.INTERNAL, car_data['message']) #Return error if Flask returns an error.
                return

            cars = car_data['data']['cars']

            cars_in_geofence = []
            for car in cars:
                if is_within_geofence(user_lat, user_lon, car['latitude'], car['longitude']):
                    cars_in_geofence.append(geofence_pb2.Car(
                        id=car['id'], make=car['make'], model=car['model'], year=car['year'], color=car['color'], price_per_hour=car['price_per_hour'], available=car['available'], latitude=car['latitude'], longitude=car['longitude']
                    ))

            return geofence_pb2.CarList(cars=cars_in_geofence)

        except requests.exceptions.RequestException as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error calling Flask API: {e}")
            return

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    geofence_pb2_grpc.add_GeofenceServiceServicer_to_server(GeofenceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()