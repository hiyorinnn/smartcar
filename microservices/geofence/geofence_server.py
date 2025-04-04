import grpc
import requests
import geofence_pb2
import geofence_pb2_grpc
from concurrent import futures

from invokes import invoke_http

def is_within_geofence(user_lat, user_lon, car_lat, car_lon, radius=0.023): #Change radius to define the geofence
    # Simple distance calculation 
    return (user_lat - car_lat)**2 + (user_lon - car_lon)**2 <= radius**2

class GeofenceServicer(geofence_pb2_grpc.GeofenceServiceServicer):
    def GetCarsInGeofence(self, request, context):
        user_lat = request.user_latitude
        user_lon = request.user_longitude

        try:
            # Make an API call to car_avaliability microservice
            car_data = self.get_all_available_car()

            if car_data['code'] != 200:
                context.abort(grpc.StatusCode.INTERNAL, car_data['message']) #Return error if Flask returns an error.
                return

            cars = car_data['data']['cars']

            cars_in_geofence = []
            for car in cars:
                if is_within_geofence(user_lat, user_lon, car['latitude'], car['longitude']):
                    cars_in_geofence.append(geofence_pb2.Car(
                        id=car['id'], make=car['make'], model=car['model'], year=car['year'], color=car['color'], price_per_hour=car['price_per_hour'], available=car['available'], latitude=car['latitude'], longitude=car['longitude'], town=car['town']
                    ))

            return geofence_pb2.CarList(cars=cars_in_geofence)

        except requests.exceptions.RequestException as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error calling Flask API: {e}")
            return
        
    def GetCarsInLocation(self, request, context):
        location = request.location
        try:
            # Make an API call to car_avaliability microservice
            car_data = self.get_all_available_car()

            if car_data['code'] != 200:
                context.abort(grpc.StatusCode.INTERNAL, car_data['message']) #Return error if Flask returns an error.
                return

            cars = car_data['data']['cars']

            cars_in_location = []
            for car in cars:
                if car['town'].lower() == location.lower():
                    cars_in_location.append(geofence_pb2.Car(
                        id=car['id'], make=car['make'], model=car['model'], year=car['year'], color=car['color'], price_per_hour=car['price_per_hour'], available=car['available'], latitude=car['latitude'], longitude=car['longitude'], town=car['town']
                    ))

            return geofence_pb2.CarList(cars=cars_in_location)

        except requests.exceptions.RequestException as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Error calling Flask API: {e}")
            return

    def get_all_available_car(self):
        # Make an API call to car_avaliability microservice
        #car_avaliable_URL = 'http://127.0.0.1:5000/car/available' #Change to URL to use with docker
        car_avaliable_URL = 'http://car_available:5000/car/available'

        print("  Invoking car_available microservice...")
        car_available_result = invoke_http(
            car_avaliable_URL, method="GET"
        )
        print(f"  car_avaliable_result:{car_available_result}\n")
        return car_available_result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    geofence_pb2_grpc.add_GeofenceServiceServicer_to_server(GeofenceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()