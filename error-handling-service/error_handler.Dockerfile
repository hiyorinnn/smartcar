# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to install dependencies
COPY requirements.txt .

# Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the port for the Flask app
EXPOSE 5005

# Command to run the Flask application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5005", "error_handler:app"]


