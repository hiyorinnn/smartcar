from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pika
from os import environ

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/car_service"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Car(db.Model):
    __tablename__ = "car_available"  # Ensure consistency with SQL schema

    id = db.Column(db.String(13), primary_key=True)
    make = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(64), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)  
    available = db.Column(db.Boolean, default=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False) 
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    town = db.Column(db.String(50), nullable = False)

    def __init__(self, id, make, model, year, color, price_per_hour, latitude, longitude,town,available=True):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.price_per_hour = price_per_hour
        self.available = available
        self.latitude = latitude
        self.longitude = longitude 
        self.town = town

    def json(self):
        return {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "color": self.color,
            "price_per_hour": self.price_per_hour,  
            "available": self.available,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude),  
            "town": self.town
        }


# REST API Routes

# Get all cars

@app.route("/car")
def get_all():
    carlist = db.session.scalars(db.select(Car)).all()

    if carlist:
        return jsonify(
            {
                "code": 200,
                "data": {"cars": [car.json() for car in carlist]},
            }
        )
    return jsonify({"code": 404, "message": "There are no cars."}), 404


# Get available cars
@app.route("/car/available")
def get_available():
    carlist = db.session.scalars(db.select(Car).filter_by(available=True)).all()

    if carlist:
        return jsonify(
            {
                "code": 200,
                "data": {"cars": [car.json() for car in carlist]},
            }
        )
    return jsonify({"code": 404, "message": "There are no available cars."}), 404

# Get car by id
@app.route("/car/<string:id>")
def find_by_id(id):
    car = db.session.scalar(db.select(Car).filter_by(id=id))

    if car:
        return jsonify({"code": 200, "data": car.json()})
    return jsonify({"code": 404, "message": "Car not found."}), 404

#Update car availability
@app.route("/car/<string:id>/availability", methods=["PUT"])
def update_availability(id):
    car = db.session.scalar(db.select(Car).filter_by(id=id))

    if not car:
        return jsonify({"code": 404, "message": "Car not found."}), 404

    data = request.get_json()
    if 'available' not in data:
        return jsonify({"code": 400, "message": "Missing 'available' field in request."}), 400

    try:
        car.available = data['available']
        db.session.commit()
    except Exception as e:
        print("Exception:{}".format(str(e)))
        return (
            jsonify(
                {
                    "code": 500,
                    "data": {"id": id},
                    "message": "An error occurred updating the car availability.",
                }
            ),
            500,
        )

    return jsonify({"code": 200, "data": car.json()})


if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Start Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
