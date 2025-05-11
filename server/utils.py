import bson
import json

def safe_bson(bson_obj):
    '''
    Converts a bson object (with some non-json items) and converts it to a json object
    '''
    json_string = bson.json_util.dumps(bson_obj)
    json_obj = json.loads(json_string)

    return json_obj
