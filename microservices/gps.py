import requests
from flask import Flask, jsonify, request

app = Flask(__name__)



@app.route('/api/ip_location', methods=['GET'])
def get_ip_location():
    # test_ip = "8.8.8.8" #google's public DNS.
    # # test_ip = request.remote_addr #use this in production to get client's IP
    try:
        # ip = requests.get('http://localhost:8000/api/ipify').text
        # print('My public IP address is: {}'.format(ip))

        response = requests.get(f'https://ipinfo.io/json')
        response.raise_for_status() #check for errors.
        
        data = response.json()
        
        if data:
            latitude, longitude = map(float, data['loc'].split(','))
            return jsonify({
                'latitude': latitude,
                'longitude': longitude,
                'city': data['city'],
                'country': data['country'],
            })
        else:
            return jsonify({'error': data['message']}), 400

    except requests.exceptions.RequestException as e:
            return jsonify({'error': f'API request failed: {e}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)