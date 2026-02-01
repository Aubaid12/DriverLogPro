from datetime import datetime, timedelta
import random

class TripScheduler:
    def __init__(self, start_time, cycle_used_hours=0):
        self.current_time = start_time
        # cycle_used_hours is the amount used in the last 7 days + today so far (before this trip)
        self.cycle_used = cycle_used_hours
        self.events = []
        
        self.drive_time_today = 0
        self.on_duty_time_start = self.current_time
        self.drive_time_continuous = 0
        self.miles_since_fuel = 0
        
        # Track daily on-duty totals for 70/8 rule
        # Simplified: We just add to a running total since we don't have full 8-day history
        self.cycle_used_at_start = cycle_used_hours
        
    def add_event(self, status, duration_minutes, location, remark):
        start = self.current_time
        end = start + timedelta(minutes=duration_minutes)
        self.events.append({
            "status": status,
            "start": start,
            "end": end,
            "duration": duration_minutes,
            "location": location,
            "remark": remark
        })
        self.current_time = end
        
        # Update HOS Counters
        if status == 3: # Driving
            self.drive_time_today += (duration_minutes / 60.0)
            self.drive_time_continuous += (duration_minutes / 60.0)
            self.cycle_used += (duration_minutes / 60.0)
        elif status == 4: # On Duty
            self.cycle_used += (duration_minutes / 60.0)
            # On Duty event >= 30 mins counts as a break (FMCSA rule)
            if duration_minutes >= 30:
                self.drive_time_continuous = 0
                
        elif status in [1, 2]: # Off duty / Sleeper
            if duration_minutes >= 600: # 10 hr reset
                 self.reset_clocks()
            if duration_minutes >= 30:
                self.drive_time_continuous = 0
            # 34-hour restart (Simplified check)
            if duration_minutes >= 2040: # 34 * 60
                self.cycle_used = 0

    def reset_clocks(self):
        self.drive_time_today = 0
        self.drive_time_continuous = 0
        self.on_duty_time_start = self.current_time

    def check_break_needed(self, needed_drive_hours):
        if self.drive_time_continuous + needed_drive_hours > 8:
            return True, (8 - self.drive_time_continuous)
        return False, 0

    def check_reset_needed(self, needed_drive_hours, needed_total_hours):
        # 11 hour driving limit
        if self.drive_time_today + needed_drive_hours > 11:
            return True
        # 14 hour window check
        window_elapsed = (self.current_time - self.on_duty_time_start).total_seconds() / 3600
        if window_elapsed + needed_total_hours > 14:
            return True
        return False
        
    def check_cycle_violation(self):
        # 70 hours in 8 days
        if self.cycle_used > 70:
            return True
        return False

    def _get_state(self, loc_str):
        if not loc_str: return ""
        parts = loc_str.replace(',', ' ').split()
        # Simple heuristic: last part that is 2 chars uppercase
        for part in reversed(parts):
            if len(part) == 2 and part.isupper() and part.isalpha():
                return part
        return ""

    def drive_leg(self, distance_miles, duration_hours, start_loc, end_loc):
        avg_speed = distance_miles / duration_hours if duration_hours > 0 else 50
        
        remaining_miles = distance_miles
        remaining_hours = duration_hours
        
        start_state = self._get_state(start_loc)
        end_state = self._get_state(end_loc)
        
        loop_guard = 0
        while remaining_miles > 0:
            loop_guard += 1
            if loop_guard > 500: # increased guard for long trips
                break
            
            # Check Fuel
            if self.miles_since_fuel + remaining_miles > 1000:
                # Need fuel before destination?
                dist_can_drive = 1000 - self.miles_since_fuel
                if dist_can_drive < remaining_miles:
                    # Drive to fuel stop
                    drive_hrs = dist_can_drive / avg_speed
                    # We will handle this by shortening the step below if needed, 
                    # but actually we can just rely on the step loop logic if we cap step_miles
                    pass 

            # Step determination
            step_hours = min(1, remaining_hours)
            if step_hours < 0.1: step_hours = remaining_hours
            step_miles = step_hours * avg_speed
            
            # 1. Fuel Check during step
            if self.miles_since_fuel + step_miles > 1000:
                # Drive only until fuel needed
                miles_to_fuel = 1000 - self.miles_since_fuel
                hours_to_fuel = miles_to_fuel / avg_speed
                if hours_to_fuel > 0.01:
                    step_hours = hours_to_fuel
                    step_miles = miles_to_fuel
                    # After this step we WILL fuel
            
            # 2. Break Check
            break_needed, time_til_break = self.check_break_needed(step_hours)
            if break_needed and time_til_break < step_hours:
                partial_hours = max(0, time_til_break)
                if partial_hours > 0.01:
                    # Determine location for this short drive
                    # Simple interpolation of state? 
                    curr_state = start_state if remaining_miles > (distance_miles/2) else end_state
                    if not curr_state: curr_state = "US"
                    hwy_num = random.randint(1, 99)
                    
                    self.add_event(3, partial_hours*60, f"Highway I-{hwy_num}, {curr_state}", "Driving")
                    remaining_hours -= partial_hours
                    remaining_miles -= (partial_hours * avg_speed)
                    self.miles_since_fuel += (partial_hours * avg_speed)
                
                self.add_event(1, 30, "Rest Area", "30-min Rest Break")
                continue
            
            # 3. Daily Reset Check (11/14 rule)
            if self.check_reset_needed(step_hours, step_hours):
                self.add_event(2, 600, "Truck Stop", "10-hour Sleeper Berth Reset")
                continue

            # 4. Weekly Cycle Check
            # If adding this drive puts us over 70...
            if self.cycle_used + step_hours > 70:
                # We need a 34 hour restart!
                self.add_event(1, 2040, "Truck Stop", "34-Hour Cycle Restart")
                continue

            # If all safe, Drive
            # Safety check: ensure we move forward
            if step_hours < 0.001:
                 # Force a minimal step to avoid infinite loop
                 step_hours = 0.001
            
            # Dynamic Location
            # rough proxy for progress
            curr_state = start_state if remaining_miles > (distance_miles/2) else end_state
            if not curr_state: curr_state = "US"
            hwy_num = random.randint(1, 99)
            loc_str = f"Highway I-{hwy_num}, {curr_state}"
            
            self.add_event(3, step_hours*60, loc_str, "Driving")
            
            # Update counters
            remaining_hours -= step_hours
            step_miles_actual = (step_hours * avg_speed) # Re-calculate based on final step_hours
            remaining_miles -= step_miles_actual
            self.miles_since_fuel += step_miles_actual
            
            # Post-Drive actions
            if self.miles_since_fuel >= 1000:
                # Fueling event
                self.add_event(4, 30, "Fuel Station", "Fueling - On Duty")
                self.miles_since_fuel = 0
        
        self.add_event(4, 15, end_loc, "Arrived / Post-Trip")

def generate_plan(start_loc, pickup_loc, dropoff_loc, current_cycle_used):
    pass

