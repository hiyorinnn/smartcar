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
AWS_ACCESS_KEY = 'ASIAZVRFQWBSQL43XJ6W'
AWS_SECRET_KEY = 'okBT8nYRfii3dnXHbhD130SgTt8u8lssWcYUlrbD'
AWS_SESSION_TOKEN = 'IQoJb3JpZ2luX2VjELb//////////wEaCXVzLXdlc3QtMiJHMEUCIQCDcw+gdxlUc1Tn2IecY+QVnPe469UrMfKxAUESpgb9vgIgV/ZgWBybZEB8jKRHGPhc47k+c0NN0+UNJ5Nt9oyyiWAquAIILxAAGgw2NjQ3MjQ4Nzc0MTMiDE+ZqWFeit0zOycfrCqVAsqmER5h2nMrNu3eRaH8J9nibi5oB60Fs5TpHsX02OrkA9R99bCqfU951hm64VddAqq/9WfVXxWXNe7WGBpmMePEMZGhz2oKSZHNzluIREGyCEUhvyzj7ZNubyesin6RvXSX94Vkvri5J5DNaNO4Q6t1/PckwfvnkjXV6+4L3lRBg/yGh4saKY5SkHkZ2Guckzy5ZJ+i0Ve1iaDylJGzuTYlHNj45+nLiCH1TJhiGBxdwQ142UDYJ1Quv/NgV8mfPzyA72JfcYfoPNlPGu1eslMK9dVFh0X0YE0ZIKDhAHV0cmDRN2rO4MKV88N9Y1pVn8l30vxdjZqC8AasC5Np++pxD1+CO46VNcQYDqhkLmMIY3SmbyIwkODEvwY6nQHZvuRH1PiYaCK4VegC6HX61TXV5dqqzTpF24+eP4mGBYeUgskFUXcunKzsTyzOuo3HXOSefj2WsRI7/c1FTeUQdrQWSpsHe2mCcyssDZlafJz6XIDX/jkzwe/iT23hHp6UvIxYX7CYYrcis5GQltK2T8OOTtk5XQexj6dLUFiUmrjuvDICOS0/6QtKbe8HzRyBgRC+2boGkSrEmk0Q'

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
    region_name=AWS_REGION,
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

        booking_id = data.get('booking_id')  # Extract the booking ID
        images = data.get('images')  # Extract the images dictionary

        # Check if the required fields are present
        if not booking_id or not images:
            return jsonify({'error': 'Missing booking_id or images'}), 400

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
        return jsonify({'booking_id': booking_id, 'presigned_urls': presigned_urls})

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
    
    # Extract the 'booking_id' and 'presigned_urls' from the request JSON
    booking_id = data.get('booking_id')
    presigned_urls = data.get('presigned_urls')  # This should be a list or dict of presigned URLs

    if not booking_id or not presigned_urls:
        return jsonify({"error": "booking_id and presigned_urls are required"}), 400

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
