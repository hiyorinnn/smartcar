from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3
import io
from botocore.exceptions import NoCredentialsError, ClientError
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
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

# Helper Function to Display Image with Bounding Boxes (for Rekognition)
def display_image(bucket, photo, response):
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket, photo)
    s3_response = s3_object.get()
    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    for customLabel in response['CustomLabels']:
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']
            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            draw.text((left, top), customLabel['Name'], fill='#00d400', font=fnt)

            points = (
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top)
            )
            draw.line(points, fill='#00d400', width=5)

    image.show()

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

@app.route('/generate_presigned_url', methods=['GET'])
def generate_presigned_url():
    file_name = request.args.get('file_name')  # Get the file name from the request
    file_type = request.args.get('file_type')  # Get the file type (MIME type)

    try:
        # Generate a pre-signed URL to upload a file to S3
        response = s3_client.generate_presigned_url('put_object',
                                                   Params={'Bucket': S3_BUCKET_NAME,
                                                           'Key': file_name,
                                                           'ContentType': file_type},
                                                   ExpiresIn=3600)  # URL expires in 1 hour

        return jsonify({
            'url': response,
            'bucket': S3_BUCKET_NAME,
            'file_name': file_name,
            'file_type': file_type
        })
    
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 403
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rekognition', methods=['GET'])
def detect_labels():
    # Get the 'bucket' and 'photo' from query parameters in the request
    bucket = "esmbucketmicroservice"
    photo = request.args.get('file_name')  # e.g., 'assets/carDefects/1742101211/su_2949.jpg'

    if not bucket or not photo:
        return jsonify({"error": "Bucket and photo parameters are required"}), 400

    # The model ARN can be static (or dynamic if needed)
    model = 'arn:aws:rekognition:us-east-1:664724877413:project/carDefects/version/carDefects.2025-03-16T13.03.35/1742101419563'
    min_confidence = 50

    # Call the function to detect custom labels
    custom_labels = show_custom_labels(model, bucket, photo, min_confidence)
    label_count = len(custom_labels)

    # Return custom labels in JSON format
    return jsonify({
        "CustomLabels": custom_labels,
        "LabelCount": label_count
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="5000")
