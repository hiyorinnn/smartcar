FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors flask-sqlalchemy mysql-connector-python

# Copy application code
COPY booking_log.py .

# Set environment variables
ENV PORT=5006
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 5006

# Command to run the application
CMD ["python", "booking_log.py"]