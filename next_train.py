import http.client, urllib.request, urllib.parse, urllib.error, base64, json, os, datetime, sys

arrows = {
        'north': '↑',
        'south': '↓',
        'east': '→',
        'west': '←',
        }

pretty_lines = {
        'RD': 'Red',
        'SV': 'Silver',
        'OR': 'Orange',
        'BL': 'Blue',
        'YL': 'Yellow',
        'GR': 'Green',
        }

pretty_statuses = {
        'BRD': 'Boarding',
        'ARR': 'Arriving',
        }

def filter_join(components):
    filtered = list(filter(lambda s: s is not None, components))
    return " ".join(filtered)

def get_trains_by_direction(trains, direction):
    return list(filter(lambda train: train['DestinationName'] in direction['destinations'], trains))

def create_direction_str(direction, all_trains, lines):
    dir_trains = get_trains_by_direction(all_trains, direction)
    if (len(dir_trains) > 0):
        arrow = arrows[direction['name']]
        next_train = dir_trains[0]
        line = f"({pretty_lines.get(next_train.get('Line'), next_train.get('Line'))})" if (len(lines) > 1) else None
        status = next_train.get('Min')
        pretty_status = f"{status} min" if status.isdigit() else pretty_statuses.get(status, status)
        return filter_join([arrow, pretty_status, line])

def get_all_trains(location):
    try:
        headers = {
            'api_key': os.environ['WMATA_KEY'],
        }
        params = urllib.parse.urlencode({})
        conn = http.client.HTTPSConnection('api.wmata.com')
        conn.request("GET", f"/StationPrediction.svc/json/GetPrediction/{location['code']}?{params}", "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        data_dict = json.loads(data.decode('utf-8'))
        return data_dict['Trains']
    except Exception as e:
        print(f"Error {e}")

if __name__ == "__main__":
    locations = {}
    with open('locations.json') as f:
        locations = json.load(f)
    if locations:
        location = locations.get(sys.argv[1], {})
        trains = get_all_trains(location)
        statuses = [create_direction_str(dir, trains, location['lines']) for dir in location['directions']]
        if (len(statuses) > 0):
            str_list = list(filter(lambda s: s is not None, statuses))
            display_string = " ".join(str_list)
            print(display_string)
