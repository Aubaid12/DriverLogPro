import requests
import json
import base64

url = "http://localhost:8000/api/generate-plan/"
data = {
    "current_location": "Green Bay, WI",
    "pickup_location": "Chicago, IL",
    "dropoff_location": "St. Louis, MO",
    "cycle_used": 0
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        res_json = response.json()
        print("Keys:", res_json.keys())
        print("Itinerary Items Count:", len(res_json.get('itinerary', [])))
        
        # Print first 20 and last 20 items to see the loop
        items = res_json.get('itinerary', [])
        for i, item in enumerate(items):
            if i < 10 or i > len(items) - 10:
                print(f"{i}: {item}")
        
        # Save Images
        if res_json.get('log_images'):
            print("Image Data Length:", len(res_json['log_images'][0]))
            
        # Save PDF
        if res_json.get('pdf_blob'):
            pdf_bytes = base64.b64decode(res_json['pdf_blob'])
            with open("test_output.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("Successfully saved test_output.pdf")
        else:
            print("No PDF blob returned")
            
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
