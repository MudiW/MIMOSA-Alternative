# Importing necessary modules and packages
from flask import Flask, render_template, jsonify, request
import db
import requests
import time

# Creating a Flask application instance
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# Route to the home page of the web application
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle GET and POST requests for items
@app.route('/api/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        # If the request method is GET, read data from the database and return as JSON
        items = db.read_items()
        return jsonify(items)
    elif request.method == 'POST':
        # If the request method is POST, add new item to the database and return the item as JSON
        item = request.get_json()
        id = db.write_item(item)
        item['id'] = id
        return jsonify(item)


# Route to handle GET, PUT, DELETE and POST requests for an individual item
@app.route('/api/items/<id>', methods=['GET', 'PUT', 'DELETE', 'POST'])
def item(id):
    item = db.get_item(id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    if request.method == 'GET':
        # If the request method is GET, return the item as JSON
        return jsonify(dict(item))
    elif request.method == 'PUT':
        # If the request method is PUT, update the item in the database and return the updated item as JSON
        db.update_item(id, request.get_json())
        item = db.get_item(id)
        return jsonify(dict(item))
    elif request.method == 'DELETE':
        # If the request method is DELETE, remove the item from the database and return a success message as JSON
        db.delete_item(id)
        return jsonify({'success': True})
    elif request.method == 'POST':
        # If the request method is POST, check if the request is for locating the item, and send the position to a WLED API
        if request.form.get('action') == 'locate':
            lights(item['position'], item['ip'])
            print(f"Position of {item['name']}: {item['position']}: {item['ip']}")
            return jsonify({'success': True})
        elif request.form.get('action') == 'addQuantity':
            item['quantity'] += 1
            db.update_item(id, item)
            return jsonify({'success': True})
        elif request.form.get('action') == 'removeQuantity':
            item['quantity'] -= 1
            db.update_item(id, item)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid action'}), 400


# Route to handle DELETE requests for an individual item
@app.route('/api/items/<id>', methods=['DELETE'])
def delete_item(id):
    db.delete_item(id)
    return jsonify({'success': True})

def send_reset1(target_ip, start_num, stop_num, color,fx,pal):
    url = f"http://{target_ip}/json/state"  # construct URL using the target IP address
    state = {"seg": [{"id": 0, "start": start_num, "stop": stop_num, "col": [color],"fx": fx,"pal": pal, "bri": 255}]}
    response = requests.post(url, json=state)


def send_reset2(target_ip, start_num, stop_num, color,fx,pal):
    url = f"http://{target_ip}/json/state"  # construct URL using the target IP address
    state = {"seg": [{"id": 1, "start": start_num, "stop": stop_num, "col": [color],"fx": fx,"pal": pal,"bri": 255}]}
    response = requests.post(url, json=state)

def send_request2(target_ip, start_num, stop_num, color,fx):
    url = f"http://{target_ip}/json/state"  # construct URL using the target IP address
    state = {"seg": [{"id": 0, "start": start_num, "stop": stop_num, "col": [color],"fx": fx,"bri": 70}]}
    response = requests.post(url, json=state)


def send_request(target_ip, start_num, stop_num, color,fx):
    url = f"http://{target_ip}/json/state"  # construct URL using the target IP address
    state = {"seg": [{"id": 1, "start": start_num, "stop": stop_num, "col": [color],"fx": fx,"bri": 255}]}
    response = requests.post(url, json=state)


def lights(position, pi):
    start_num = int(position) - 1
    send_request2(pi, 0, 64, [255, 0, 0],0)
    send_request(pi, start_num, int(position), [0, 255, 0],0)
    time.sleep(5)  # Change how long the LED stays on for.
    send_reset1(pi, 0, 64, [0, 255, 0],15,27)
    send_reset2(pi, 0, 64, [0, 255, 0],15,27)

# Running the Flask application
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
