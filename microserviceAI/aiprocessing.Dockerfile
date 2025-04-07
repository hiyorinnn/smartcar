# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set environment variables to avoid Python writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 5003

# Command to run the app
CMD ["python", "aiprocessing.py"]
