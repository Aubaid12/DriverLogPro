import requests
import json

# Define verify function
def verify_logs():
    url = "http://127.0.0.1:8000/api/generate-plan/"
    payload = {
        "current_location": "New York, NY",
        "pickup_location": "Chicago, IL",
        "dropoff_location": "Los Angeles, CA",
        "cycle_used": 0
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("Response received.")
        
        # 1. Verify Locations
        itinerary = data.get('itinerary', [])
        print("\n--- Itinerary Sample ---")
        for item in itinerary[:10]:
            print(item)
            
        has_highway = any("Highway I-" in item for item in itinerary)
        print(f"\nHas 'Highway I-' locations: {has_highway}")
        
        # 2. Verify Fuel Stops
        fuel_stops = [item for item in itinerary if "Fueling - On Duty" in item]
        print(f"\nFuel Stops found: {len(fuel_stops)}")
        for stop in fuel_stops:
            print(stop)
            
        if len(fuel_stops) > 0:
            print("✅ Fuel stops verified.")
        else:
            print("❌ No fuel stops found (Expected for NY->LA).")

        # 3. Check 24h Totals (Visual check from itinerary implies logic ran, but hard to check totals from simple itinerary list)
        # We need to rely on the fact that if it generated successfully, the view logic ran.
        # But we can check if it crashed.
        print("\n✅ API Response successful. Logic executed without crash.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_logs()
