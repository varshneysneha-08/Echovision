import requests
import json

AZURE_MAPS_KEY = "Enter your key here"    # Replace with your actual key

def get_coords(location):
    url = "https://atlas.microsoft.com/search/address/json"
    params = {
        'subscription-key': AZURE_MAPS_KEY,
        'api-version': '1.0',
        'query': location,
        'limit': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('results'):
        position = data['results'][0]['position']
        return position['lat'], position['lon']
    return None, None

def get_route(start, end):
    start_lat, start_lon = get_coords(start)
    end_lat, end_lon = get_coords(end)

    if None in [start_lat, start_lon, end_lat, end_lon]:
        print("Could not find coordinates for one or both locations.")
        return

    print(f"Start coords: {start_lat}, {start_lon}")
    print(f"End coords: {end_lat}, {end_lon}")

    route_url = (
        "https://atlas.microsoft.com/route/directions/json"
        f"?subscription-key={AZURE_MAPS_KEY}"
        f"&api-version=1.0"
        f"&query={start_lat},{start_lon}:{end_lat},{end_lon}"
        f"&instructionsType=text"
        # Remove routeRepresentation param to get full details
    )

    response = requests.get(route_url)
    data = response.json()

    print("Full Route API Response:")
    print(json.dumps(data, indent=2))

    if 'routes' in data and len(data['routes']) > 0:
        legs = data['routes'][0].get('legs', [])
        if legs:
            for leg in legs:
                instructions = leg.get('instructions', [])
                print("\nInstructions:")
                for step in instructions:
                    print(f"- {step['text']} (Distance: {step['lengthInMeters']} meters)")
        else:
            print("No legs found in route data.")
    else:
        print("No routes found in response.")

if __name__ == "__main__":
    start_location = "quarsi aligarh uttar pradesh india"
    end_location = "aligarh muslim university uttarpradesh india"
    get_route(start_location, end_location)





