# All the dependencies/imports
from botocore.exceptions import NoCredentialsError, ClientError
from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3

app = Flask(__name__)

# To change
CORS(app, origins=["http://127.0.0.1:5500"])

# Set your S3 bucket name and AWS region
AWS_REGION = 'us-east-1'
S3_BUCKET_NAME = 'esmbucketmicroservice'
AWS_ACCESS_KEY = 'ASIAZVRFQWBSUHDHALV4'
AWS_SECRET_KEY = 'zcqn6598O1zBeOfFW6hSThjmg9AZEmXj43X5Htka'
AWS_SESSION_TOKEN = 'IQoJb3JpZ2luX2VjEBcaCXVzLXdlc3QtMiJHMEUCIFGpSxeFAemIf4hpO8ATYWAtffKcLxlew5WFn+XyRylCAiEA3hm7qPN96nGfwU/d5hgxnLrBsFrWLmbjurgN4YkTJlMquAIIcBAAGgw2NjQ3MjQ4Nzc0MTMiDKEpj7j74s/yO0X/9iqVAvSbMzwZgiM9uVhoSeq41HXMjTHW7yWW0Q+HGgiH4rbHDPwGK8tLkhT0GUuKXs9M0MCGUCorHFcITgBBEznrqwLc49SiuIzBbikMmdAsV7CjvvmXL0nDUm7gzAhir41AEZS5CiDW3WB2WA4MRzgT7SDPWFcpbZsF32/4raONcSaLjHVhgX/WnqCz9ZuYvmRNlm0p3S/maXjAJgd1KfEXNyOgvoAiSB4zofG7Xf6faP5bWMCvqjGWMTk6Lgg1t20uu1xFCYdb66Kwl5iosMACGtT0uby3ojI2EveL/AU48k3JmDrlYx0yunV0zWmAt5ZhOcMX++gYoEIStGyAGgU6eLpmI+HNwUu20fE6u7AI7AjgdHaL56sw0NjpvgY6nQH1C2Hbm4+S7efQ2SVZLaHBFHkHfoLhYcgOSf14IXaCEP3wcklT42rQo8SW0/qYYId0lqGQZhlp3gGdQUvNMzKE3UK+004HVtvM8hhWTgBnW8pMa3nZ8J/JFSDsXWYw4/j0MtOsWZ6AH1ce+hNyAZwcMLUyjty6WcwbgWp4c0v3nqEQYeeViY8+DBZSfMeX/q8C5lNLwDqGqmdmhJPv'

# Initialize the S3 client with boto3
s3_client = boto3.client(
    's3', 
    region_name=AWS_REGION, 
    aws_access_key_id=AWS_ACCESS_KEY, 
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# AWS Rekognition Client Setup
rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

# Function to Detect Custom Labels and Return them
def show_custom_labels(model, bucket, photo, min_confidence):
    response = rekognition_client.detect_custom_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model
    )

    custom_labels = []
    if 'CustomLabels' in response:
        for customLabel in response['CustomLabels']:
            custom_labels.append({
                'Label': customLabel['Name'],
                'Confidence': customLabel['Confidence']
            })

    return custom_labels

@app.route('/api/generate-presigned-url', methods=['POST'])
def generate_presigned_url():
    try:
        # Get the data from the request (assuming it's a JSON payload)
        data = request.get_json()

        booking_id = data.get('bookingID')  # Extract the booking ID
        images = data.get('images')  # Extract the images dictionary

        # Check if the required fields are present
        if not booking_id or not images:
            return jsonify({'error': 'Missing bookingID or images'}), 400

        presigned_urls = []  # List to store the generated URLs

        # Iterate through each image and generate a pre-signed URL
        for image_key, image_data in images.items():
            file_name = image_data.get('file_name')
            file_type = image_data.get('file_type')

            if not file_name or not file_type:
                return jsonify({'error': f'Missing file_name or file_type for {image_key}'}), 400

            # Generate a pre-signed URL for each image
            response = s3_client.generate_presigned_url('put_object',
                                                       Params={'Bucket': S3_BUCKET_NAME,
                                                               'Key': f'{booking_id}/{file_name}',
                                                               'ContentType': file_type},
                                                       ExpiresIn=3600)  # URL expires in 1 hour

            # Append the generated URL to the list
            presigned_urls.append({
                'image_key': image_key,
                'presigned_url': response,
                'bucket': S3_BUCKET_NAME,
                'file_name': file_name,
                'file_type': file_type
            })

        # Return the generated URLs as a JSON response
        return jsonify({'bookingID': booking_id, 'presigned_urls': presigned_urls})

    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 403
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rekognition', methods=['POST'])  # Use POST since you are sending a payload
def detect_labels():

    # Bucket used
    BUCKET = "esmbucketmicroservice"

    # Get the data from the request
    data = request.get_json()
    
    # Extract the 'bookingID' and 'presigned_urls' from the request JSON
    booking_id = data.get('bookingID')
    presigned_urls = data.get('presigned_urls')  # This should be a list or dict of presigned URLs

    if not booking_id or not presigned_urls:
        return jsonify({"error": "bookingID and presigned_urls are required"}), 400

    # The model ARN can be static (or dynamic if needed)
    MODEL = 'arn:aws:rekognition:us-east-1:664724877413:project/carDefects/version/carDefects.2025-03-16T13.03.35/1742101419563'

    defect_count = 0  # Counter to track images with defects

    # Iterate over the presigned URLs to detect labels for each photo
    for image_data in presigned_urls:
        photo_url = image_data.get('presigned_url')  # Extract the actual URL from each image data

        if not photo_url:
            continue  # Skip if there is no URL

        # Call the function to detect custom labels for each photo
        custom_labels = show_custom_labels(MODEL, BUCKET, photo_url)

        # Check if "defects" is present in custom_labels
        if "defects" in custom_labels:
            defect_count += 1  # Increment the defect count if "defects" is found

    # Return the count of images with defects
    return jsonify({"defect_count": defect_count}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="5003")
