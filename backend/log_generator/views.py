from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import base64
from datetime import datetime

from .services.routing import geocode, get_route
from .services.hos_logic import TripScheduler
from .services.pdf_drawer import LogSheetDrawer

class GeneratePlanView(APIView):
    def post(self, request):
        try:
            data = request.data
            current_loc_str = data.get('current_location')
            pickup_loc_str = data.get('pickup_location')
            dropoff_loc_str = data.get('dropoff_location')
            cycle_used = float(data.get('cycle_used', 0))
            
            curr_coords = geocode(current_loc_str)
            pick_coords = geocode(pickup_loc_str)
            drop_coords = geocode(dropoff_loc_str)
            
            if not (curr_coords and pick_coords and drop_coords):
                return Response({"error": "Could not geocode locations"}, status=status.HTTP_400_BAD_REQUEST)
                
            route_1 = get_route(curr_coords, pick_coords)
            route_2 = get_route(pick_coords, drop_coords)
            
            if not (route_1 and route_2):
                 return Response({"error": "Could not find routes"}, status=status.HTTP_400_BAD_REQUEST)
                 
            scheduler = TripScheduler(start_time=datetime.now(), cycle_used_hours=cycle_used)
            
            # 1. Pre-trip (15m)
            scheduler.add_event(4, 15, current_loc_str, "Pre-trip Inspection")
            
            # 2. Drive to Pickup
            scheduler.drive_leg(route_1['distance_miles'], route_1['duration_hours'], current_loc_str, pickup_loc_str)
            
            # 3. Pickup (1hr)
            scheduler.add_event(4, 60, pickup_loc_str, "Loading")
            
            # 4. Drive to Dropoff
            scheduler.drive_leg(route_2['distance_miles'], route_2['duration_hours'], pickup_loc_str, dropoff_loc_str)
            
            # 5. Dropoff (1hr)
            scheduler.add_event(4, 60, dropoff_loc_str, "Unloading")
            
            # 6. Post-trip (15m)
            scheduler.add_event(4, 15, dropoff_loc_str, "Post-trip Inspection")
            
            # Group events by Day
            events_by_day = {}
            day_stats = {} # store miles/totals per day

            for e in scheduler.events:
                day_key = e['start'].date()
                if day_key not in events_by_day:
                    events_by_day[day_key] = []
                    day_stats[day_key] = {
                        'miles': 0,
                        'totals': [0, 0, 0, 0], # Off, SB, Drive, On
                        'remarks': [],
                        'from_city': current_loc_str, # Default start
                        'to_city': dropoff_loc_str # Default end
                    }
                
                start_hour = e['start'].hour + e['start'].minute/60.0
                duration_hours = e['duration'] / 60.0
                
                # Add to daily totals
                status_idx = e['status'] - 1 # 1-based status to 0-based index
                if 0 <= status_idx < 4:
                    day_stats[day_key]['totals'][status_idx] += duration_hours
                
                # Add to miles if driving
                if e['status'] == 3: # Driving
                     miles = duration_hours * 50.0 
                     day_stats[day_key]['miles'] += miles

                # Format Remark
                time_str = e['start'].strftime('%H:%M')
                loc = e['location']
                rem_text = e['remark']
                day_stats[day_key]['remarks'].append(f"{time_str} - {loc} - {rem_text}")

                events_by_day[day_key].append({
                    'status': e['status'],
                    'start_hour': start_hour,
                    'duration_hours': duration_hours
                })
                
                # Update From/To for the day (First event loc is From, Last is To - roughly)
                if len(events_by_day[day_key]) == 1:
                    day_stats[day_key]['from_city'] = e['location']
                day_stats[day_key]['to_city'] = e['location']

            drawer = LogSheetDrawer()
            log_images_b64 = []
            pil_images = []
            
            # Sort days
            sorted_days = sorted(events_by_day.keys())
            
            cycle_used_current = float(cycle_used) # Initialize running counter

            for day in sorted_days:
                stats = day_stats[day]
                
                # Normalize totals to ensure exactly 24.00
                # Round every component to 2 decimals first, because that's what we display
                stats['totals'] = [round(x, 2) for x in stats['totals']]
                
                total_sum = sum(stats['totals'])
                
                # Check for floating point drift or rounding gaps
                if abs(total_sum - 24.00) > 0.001:
                    diff = 24.00 - total_sum
                    # Add remaining diff to Off Duty (Status 1, Index 0)
                    stats['totals'][0] += diff
                    # Re-round to be sure
                    stats['totals'][0] = round(stats['totals'][0], 2)

                day_info = {
                    'date': str(day),
                    'miles_today': stats['miles'],
                    'carrier': "Logistics Co.",
                    'main_office': "123 Main St, Springfield",
                    'home_terminal': "456 Depot Ln, Hometown",
                    'truck_num': "1042",
                    'trailer_num': "5301",
                    'from_city': stats['from_city'],
                    'to_city': stats['to_city'],
                    'totals': stats['totals'],
                    'remarks_list': stats['remarks']
                }

                # --- Recap Calculations ---
                # Cycle Rule: 70 hours in 8 days.
                # We know 'cycle_used' at start of trip.
                # valid_cycle_used tracks the running total at start of THIS day.
                
                if day == sorted_days[0]:
                   current_day_start_cycle = float(cycle_used)
                else:
                   # For subsequent days, it's prev_day_end
                   # We need to track this loop-to-loop.
                   # Let's retroactively calculate it or just maintain a running counter in the loop?
                   # Better: maintain running counter.
                   pass # handled by running variable below

                # We need a define variable outside loop for running cycle
                
                # Hours worked today = Driving (idx 2) + On Duty (idx 3)
                hours_worked_today = stats['totals'][2] + stats['totals'][3]
                
                # 70 Hour Rule Math
                # Available Today = 70 - Used_Last_7_Days (which is our running 'cycle_used_current')
                # But wait, 'cycle_used' passed in IS "Used Last 7 Days"
                
                hours_available_today = 70.0 - cycle_used_current
                if hours_available_today < 0: hours_available_today = 0
                
                cycle_used_end = cycle_used_current + hours_worked_today
                
                hours_available_tomorrow = 70.0 - cycle_used_end
                if hours_available_tomorrow < 0: hours_available_tomorrow = 0
                
                day_info['recap'] = {
                    'limit': "70 / 8",
                    'used_last_7': cycle_used_current,
                    'available_today': hours_available_today,
                    'worked_today': hours_worked_today,
                    'total_since_start': cycle_used_end, # Simplified "Total on duty 7/8 days"
                    'available_tomorrow': hours_available_tomorrow
                }
                
                # Update for next day
                cycle_used_current = cycle_used_end
                
                img, _ = drawer.create_blank_log(day_info, "Driver")
                drawer.draw_events(img, _, events_by_day[day])
                
                # Store for API response (PNG)
                png_data = drawer.save_image(img)
                log_images_b64.append(f"data:image/png;base64,{base64.b64encode(png_data).decode('utf-8')}")
                
                # Store for PDF
                pil_images.append(img)
            
            # Generate PDF
            pdf_data = drawer.save_pdf(pil_images)
            pdf_b64 = base64.b64encode(pdf_data).decode('utf-8') if pdf_data else ""
            
            return Response({
                "itinerary": [e['remark'] + f" at {e['start'].strftime('%H:%M')}" for e in scheduler.events],
                "log_images": log_images_b64,
                "pdf_blob": pdf_b64,
                "route_geometry": {
                    "type": "FeatureCollection",
                    "features": [
                        {"type": "Feature", "geometry": route_1['geometry'], "properties": {"type": "pre-load"}},
                        {"type": "Feature", "geometry": route_2['geometry'], "properties": {"type": "load"}}
                    ]
                }
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
