import uuid
import json
import os
from datetime import datetime
from datetime import timezone
import sys

hyper_preview_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hyperlink_preview")
sys.path.append(hyper_preview_path)

# Library imports
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hyperlink_preview as HLP

app = Flask(__name__,
    static_folder='../frontend/build',
    static_url_path='')
CORS(app)


FILE = 'data.json'

def checkfile():
    datafile = os.path.join(os.path.dirname(__file__), FILE)
    if not os.path.exists(datafile):
        with open(datafile, 'w') as file:
            json.dump([], file)

    with open(datafile) as file:
        content = file.read()

    if not content:
        with open(datafile, 'w') as file:
            json.dump([], file)

    return datafile


def addToFile(link):
    # Create emtpy file if os.path does not exist
    datafile = checkfile()

    # Prepend to json file
    datestr = datetime.now(timezone.utc).isoformat()

    obj = {
        'idx': uuid.uuid4().hex,
        'link': link,
        'date': datestr,
    }

    try:
        data = readfile()
        data.insert(0, obj)

        with open(datafile, 'w') as file:
            json.dump(data, file)

        return True
    except Exception as e:
        print(f'failed to add to file with e', e)
        return False

def readfile():
    datafile = checkfile()
    with open(datafile) as file:
        content = json.load(file)

    return content

def deleteFromFile(idx):
    datafile = checkfile()
    try:
        data = readfile()
        data = [item for item in data if item['idx'] != idx]

        with open(datafile, 'w') as file:
            json.dump(data, file)

        return True
    except Exception as e:
        print(f'failed to delete from file with e', e)
        return False


# Serve React App
@app.route('/')
def serve():
    print(f'Serving static files from {app.static_folder}')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/links', methods=['GET'])
def get_signin_url():
    '''
    Get all the last N links in the board.
    '''
    # Get request args
    offset = int(request.args.get('offset') or 0)
    n = int(request.args.get('n') or 10)

    # Read from the file
    data = readfile()
    payload = data[offset:offset+n]

    # Return payload
    return jsonify(payload), 200


@app.route('/add', methods=['POST'])
def login():
    '''
    POST a link to the board.
    Will add to a file.
    '''
    # Get request args
    link = request.json.get('link')

    if not link:
        return jsonify({'error': 'No link provided'}), 400

    # Try to add to the file
    try:
        success = addToFile(link)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Server failed to post link',
            }), 500

        return jsonify({
            'success': True,
            'message': 'Added successully!',
        }), 200
    except Exception as e:
        import traceback
        print('Error posting link:', e)
        print('Full stack trace:')
        print(traceback.format_exc())
        payload = {
            'success': False,
            'message': 'Server failed to post link',
            'error': str(e),
        }
        return jsonify(payload), 500

@app.route('/delete/<idx>', methods=['DELETE'])
def delete_link(idx):
    '''
    DELETE a link from the board by its idx.
    '''
    try:
        success = deleteFromFile(idx)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Server failed to delete link',
            }), 500

        return jsonify({
            'success': True,
            'message': 'Deleted successfully!',
        }), 200
    except Exception as e:
        print('Error deleting link:', e)
        return jsonify({
            'success': False,
            'message': 'Server failed to delete link',
            'error': str(e),
        }), 500

@app.route('/preview', methods=['GET'])
def get_preview():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        preview = HLP.HyperLinkPreview(url=url)
        preview = preview.get_data()
        return jsonify(preview), 200
    except Exception as e:
        print('Error fetching preview:', e)
        return jsonify({
            'error': 'Failed to fetch preview',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=3024)
