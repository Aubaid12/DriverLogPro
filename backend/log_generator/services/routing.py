import requests

def get_route(start_coords, end_coords):
    """
    Get route from OSRM.
    coords: (lat, lon) tuple
    """
    # OSRM takes lon,lat
    start_str = f"{start_coords[1]},{start_coords[0]}"
    end_str = f"{end_coords[1]},{end_coords[0]}"
    
    url = f"http://router.project-osrm.org/route/v1/driving/{start_str};{end_str}?overview=full&geometries=geojson"
    try:
        # Add timeout!
        response = requests.get(url, timeout=3)
        data = response.json()
        
        if data["code"] != "Ok":
             raise Exception(f"OSRM Error: {data.get('code')}")
            
        route = data["routes"][0]
        return {
            "distance_miles": route["distance"] * 0.000621371,
            "duration_hours": route["duration"] / 3600,
            "geometry": route["geometry"]
        }
    except Exception as e:
        print(f"Routing Error: {e}")
        # Fallback to simple calculation if API fails
        dist = ((end_coords[0] - start_coords[0])**2 + (end_coords[1] - start_coords[1])**2)**0.5 * 69
        return {
             "distance_miles": dist,
             "duration_hours": dist / 50.0,
             "geometry": None
        }

def geocode(address):
    """
    Geocode address string to (lat, lon).
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "DriverApp/1.0"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=3)
        data = response.json()
        if data:
            # Lat/Lon are strings in Nominatim response
            return (float(data[0]['lat']), float(data[0]['lon']))
    except Exception as e:
        print(f"Geocoding Error: {e}")
    return None
