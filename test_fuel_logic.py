import sys
import os
import django
from datetime import datetime

# Setup Django environment to import backend modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from log_generator.services.hos_logic import TripScheduler

def test_fuel_logic():
    scenarios = [
        (500, 0),   # 500 miles -> 0 stops
        (1100, 1),  # 1100 miles -> 1 stop
        (2100, 2)   # 2100 miles -> 2 stops
    ]
    
    print("--- Testing Fuel Logic ---")
    
    for miles, expected_stops in scenarios:
        print(f"\nTesting {miles} miles...")
        scheduler = TripScheduler(start_time=datetime.now())
        
        # Drive the leg (assume 50mph for easy math)
        scheduler.drive_leg(distance_miles=miles, duration_hours=miles/50.0, start_loc="Start", end_loc="End")
        
        # Count fuel stops
        fuel_stops = [e for e in scheduler.events if "Fueling" in e['remark']]
        count = len(fuel_stops)
        
        if count == expected_stops:
            print(f"✅ PASS: {count} fuel stops generated.")
            # Verify duration
            for e in fuel_stops:
                if e['duration'] != 30:
                    print(f"❌ FAIL: Fuel stop duration {e['duration']} != 30")
                else:
                    print(f"✅ PASS: Fuel stop duration is 30 min.")
        else:
            print(f"❌ FAIL: Expected {expected_stops}, got {count}.")
            for e in scheduler.events:
                print(f"  - {e['remark']} at {e['start']}")

if __name__ == "__main__":
    test_fuel_logic()
