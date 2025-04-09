# SmartCar Rental Booking Application

## Overview
This webapp provides a car booking system with user management, booking logs, and car availability tracking.

## Prerequisites
- WAMP (Windows) or MAMP (Mac) for local development environment
- Docker and Docker Compose
- MySQL Workbench
- Git (for cloning the repository)

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/hiyorinnn/smartcar.git
cd smartcar
```

### 2. Set Up the Local Environment
- **For Windows users**: Start WAMP Server
- **For Mac users**: Start MAMP Server
- **For all users**: Alternatively, ensure Docker is running if you prefer to use containerized services

### 3. Database Setup
1. Open MySQL Workbench and connect to your local MySQL server
2. Run the following SQL scripts in this order:
   - `databases/user.sql` - Creates and populates the user table
   - `databases/booking_logs.sql` - Sets up the booking history
   - `databases/car_available.sql` - Creates and populates the car inventory

### 4. Docker Setup
1. Build the Docker containers (ensuring fresh build with no cached components):
   ```bash
   cd microservices
   docker-compose build --no-cache
   ```

2. Start the application containers in detached mode:
   ```bash
   docker-compose up -d
   ```

3. Verify all containers are running:
   ```bash
   docker-compose ps
   ```

### 5. Access the Application
1. Ensure Python is installed then run

   ```bash
    python -m http.server 3000
   ```

2. Access the app through 
http://localhost:3000/frontend/ 


## Application Structure
- **Frontend**: HTML/JS
- **Backend**: Python Flask
- **Database**: MySQL
- **Services**:
  - User Authentication Service
  - Booking Management Service
  - Location Service
  - Car Inventory Service
  - Car Return Service
  - Payment Service
  - Notification Service 


## Common Commands

### Stopping the Application
```bash
docker-compose down
```

### Viewing Logs
```bash
docker-compose logs -f
```

### Rebuilding After Changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

### Database Connection Issues
- Ensure MySQL is running on port 3306
- Check the database credentials in `.env` file
- Verify all SQL scripts executed successfully

### Container Startup Problems
- Check Docker logs: `docker-compose logs -f [service_name]`
- Ensure all required ports are available (3000, 3306, etc.)
- Review the `.env` file for correct configuration

### RabbitMQ Startup Problems
- The RabbitMQ container takes about 15 seconds, before it can accept connections.
- This supersedes "depend-on" in compose.yaml, 
- i.e. the dependant containers will read that RabbitMQ container has started and will activate even though it is unready.
- AMQP_Setup will also continuously restart. It can be stopped after about 30 seconds, or once it logs "Connected"
- Reason: It is not a microservice, but a single-execution python script that creates the RabbitMQ exchange and queues.
