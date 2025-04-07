import os
import io
import boto3
import base64
import urllib.parse
from flask_cors import CORS
from flask import Flask, request, jsonify
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)
CORS(app)

# AWS setup: To add in environment variables
AWS_REGION = 'us-east-1'
S3_BUCKET_NAME = 'esdbucketmicroservice'
AWS_ACCESS_KEY = 'ASIAVRUVTXJAS2UDHBDK'
AWS_SECRET_KEY = 'KS1nV2wM0+r26hK0G4lOXq+EcNAn8hTEm4fQdp4R'
AWS_SESSION_TOKEN = 'IQoJb3JpZ2luX2VjEOT//////////wEaCXVzLXdlc3QtMiJHMEUCIQDPQulT4j1aihRa0u9XlrXCCL2apF1Ss/+q9p0FPMKtSAIgNZj9NDuFqoiozFb/mQ+YbFk7bj1IcFDZHm14dXeHtwEquAIIXRAAGgwzODE0OTIxMTYwMzMiDPebXDUPAr7Qg8IkSCqVAlTlDZCYlJ8pzRHq3SkmZ4donIkqDWpmdLUFqyGs7SGhcEavUU7km5Z26siSs8NvGo9r63bTpigcoGOD/phmpTJBB6TGI3xOs7Df2fCcPgWTHs751SQDf+qJo9T+xuO3V4OrVhAHR6A7i2CE5BSwK2juiseItotuXPk/RNzActNo6A/40LKSyYJnGpvJ97bh8Ewy0eBGlhoFGqHU7d/st13dkHYP3rUeT0RAu9dfovEiEumlbFnVI8rmxmdk24nWxfemENwP9+kUSAazFvoyHlPEgoI8GuNBeAPukUsTzq/s40Y+nqGEJUSQQxmRW1uf0/pcFDirwDclZ7RZC3eDItvKxlq3tczkSii/r9ea3c9fAxb3vV8wh+3OvwY6nQH/r6A/Lzc/tk3+OLE4EPqF/kIXbJBM6kYLtfUgvki8sXWnTsVrJp4d8lv+JCifsT0FbgKCvqia6eEsZAW9ynT4apVgzmZz85NtkbtP1wQJk6f/cZK/XJEFJx4lDo2r9lKgWJoYrJS8yckbj98UCL1W57Ghq0/AXFK8HYqiSvUswa0mgc27VVp7OFEbypi1m56lgKIswCCmEleha01j'
S3_BUCKET_NAME = 'esdbucketmicroservice' 

# Initialize the S3 client with boto3
s3 = boto3.client(
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

@app.route('/api/upload', methods=['POST'])
def upload():
    data = request.get_json()
    images = data['images']
    booking_id = data.get('booking_id')

    uploaded_urls = []
    
    try:
        for i, image in enumerate(images):
            file_buffer = base64.b64decode(image['buffer'])
            file_name = f"uploads/{booking_id}_{i+1}_{image['originalname']}"

            # Upload the image to S3
            try:
                s3.upload_fileobj(
                    io.BytesIO(file_buffer),
                    S3_BUCKET_NAME,
                    file_name,
                    ExtraArgs={'ContentType': image['mimetype']}
                )
            except ClientError as e:
                print(f"Error uploading file: {e}")
                return jsonify({'error': 'Failed to upload file to S3'}), 500
            
            # Generate a pre-signed URL for the uploaded image
            response = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': file_name},
                ExpiresIn=3600  # URL expires in 1 hour
            )

            print("reached here")

            # Append the pre-signed URL to the list
            uploaded_urls.append(response)

        # Return the generated pre-signed URLs in the response
        return jsonify({'message': 'Upload successful', 'booking_id': booking_id, 'imageUrls': uploaded_urls}), 200

    except (NoCredentialsError, ClientError) as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Function to Detect Custom Labels and Return them
# Function to Detect Custom Labels and Return them
def show_custom_labels(model, bucket_name, s3_key, min_confidence):
    print(f"Bucket Name: {bucket_name}")
    print(f"S3 Key: {s3_key}")
    try:
        response = rekognition_client.detect_custom_labels(
            ProjectVersionArn=model,
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': s3_key
                }
            },
            MinConfidence=min_confidence
        )

        if 'CustomLabels' in response and response['CustomLabels']:
            customLabel = response['CustomLabels'][0]  # Get only the first label
            return {
                'Label': customLabel.get('Name'),
                'Confidence': customLabel.get('Confidence')
            }
        else:
            return {
                'Label': None,
                'Confidence': None
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise

    
@app.route('/api/rekognition', methods=['POST'])
def detect_labels():
    # Get the data from the request
    data = request.get_json()

    # Extract the 'booking_id' and 'imageUrls' from the request JSON
    booking_id = data.get('booking_id')  # This should contain the 'booking_id'
    image_urls = data.get('imageUrls')  # This should be a list of image URLs

    if not booking_id or not image_urls:
        return jsonify({"error": "booking_id and imageUrls are required"}), 400

    # The model ARN can be static (or dynamic if needed)
    model = 'arn:aws:rekognition:us-east-1:381492116033:project/esdcardefects/version/esdcardefects.2025-04-07T15.34.49/1744011292606'
    min_confidence = 50

    defect_count = 0  # Counter to track images with defects

    # Iterate over the image URLs to detect labels for each photo
    for photo_url in image_urls:
        if not photo_url:
            continue  # Skip if there is no URL

        # Extract the S3 object key from the pre-signed URL
        # Parse the URL and remove the base URL part to get the object key
        parsed_url = urllib.parse.urlparse(photo_url)
        # print(parsed_url)
        s3_key = parsed_url.path.lstrip('/')
        print(s3_key)

        # Call the function to detect custom labels for each photo
        # print(f"Processing image: {photo_url}, with min_confidence: {min_confidence}")  # Debugging line
        custom_labels = show_custom_labels(model, S3_BUCKET_NAME, s3_key, min_confidence)

        # Check if "defects" is present in custom_labels
        if custom_labels.get('Label') == 'defects':
            defect_count += 1  # Increment the defect count if "defects" is found

    # Return the count of images with defects, along with the booking_id
    return jsonify({"booking_id": booking_id, "defect_count": defect_count}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)

