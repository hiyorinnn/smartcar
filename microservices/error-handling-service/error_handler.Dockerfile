# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to install dependencies
COPY requirements.txt . 
COPY error_handler.py . 

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# Expose the port for the Flask app
EXPOSE 5005

# Command to run the Flask application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5005", "error_handler:app"]
