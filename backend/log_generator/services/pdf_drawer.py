from PIL import Image, ImageDraw, ImageFont
import io

class LogSheetDrawer:
    def __init__(self):
        # Landscape A4 roughly: 1754 x 1240
        self.width = 1754
        self.height = 1240
        self.margin_x = 50
        self.margin_y = 50
        
        # Grid settings for Landscape
        self.grid_top = 450
        self.grid_height = 200
        self.grid_width = 1400  # Wider for landscape
        self.hour_width = self.grid_width / 24
        
    def create_blank_log(self, day_info, driver_name):
        # day_info is a dict: {date, miles_today, carrier, main_office, home_terminal, truck_num, trailer_num, from_city, to_city}
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        # --- HEADER SECTION ---
        # Title
        draw.text((self.margin_x, 50), "DRIVERS DAILY LOG (24 hours)", fill="black")
        draw.text((self.width - 400, 50), "Original - File at home terminal", fill="black")
        
        # Date & Miles
        draw.text((self.margin_x + 350, 40), f"Date: {day_info.get('date', '')}", fill="black")
        draw.line([(self.margin_x + 390, 55), (self.margin_x + 550, 55)], fill="black", width=1)
        
        # From / To
        draw.text((self.margin_x, 100), "From:", fill="black")
        draw.text((self.margin_x + 60, 100), day_info.get('from_city', ''), fill="black")
        draw.line([(self.margin_x + 60, 115), (self.margin_x + 600, 115)], fill="black", width=1)
        
        draw.text((self.margin_x + 650, 100), "To:", fill="black")
        draw.text((self.margin_x + 690, 100), day_info.get('to_city', ''), fill="black")
        draw.line([(self.margin_x + 690, 115), (self.margin_x + 1300, 115)], fill="black", width=1)
        
        # Boxes for Miles (Left side)
        draw.rectangle([(self.margin_x, 150), (self.margin_x + 200, 200)], outline="black")
        draw.text((self.margin_x + 10, 205), "Total Miles Driving Today", fill="black")
        draw.text((self.margin_x + 10, 165), f"{day_info.get('miles_today', 0):.1f}", fill="black", font=None) # Default font
        
        draw.rectangle([(self.margin_x + 220, 150), (self.margin_x + 420, 200)], outline="black")
        draw.text((self.margin_x + 230, 205), "Total Mileage Today", fill="black")
        draw.text((self.margin_x + 230, 165), f"{day_info.get('miles_today', 0):.1f}", fill="black") # Assuming same for now
        
        # Truck Info
        draw.rectangle([(self.margin_x, 230), (self.margin_x + 420, 280)], outline="black")
        draw.text((self.margin_x + 10, 285), "Truck/Tractor & Trailer Numbers", fill="black")
        draw.text((self.margin_x + 10, 245), f"Truck: {day_info.get('truck_num', 'N/A')}  Trailer: {day_info.get('trailer_num', 'N/A')}", fill="black")
        
        # Carrier Info (Right side)
        right_start_x = self.margin_x + 600
        
        draw.line([(right_start_x, 160), (self.width - self.margin_x, 160)], fill="black", width=1)
        draw.text((right_start_x + 10, 140), day_info.get('carrier', 'Carrier Name'), fill="black")
        draw.text((right_start_x + 200, 165), "Name of Carrier or Carriers", fill="black")
        
        draw.line([(right_start_x, 210), (self.width - self.margin_x, 210)], fill="black", width=1)
        draw.text((right_start_x + 10, 190), day_info.get('main_office', 'Office Address'), fill="black")
        draw.text((right_start_x + 200, 215), "Main Office Address", fill="black")

        draw.line([(right_start_x, 260), (self.width - self.margin_x, 260)], fill="black", width=1)
        draw.text((right_start_x + 10, 240), day_info.get('home_terminal', 'Home Terminal Address'), fill="black")
        draw.text((right_start_x + 200, 265), "Home Terminal Address", fill="black")
        
        # --- GRID SECTION ---
        # Labels
        labels = ["1. Off Duty", "2. Sleeper", "3. Driving", "4. On Duty"]
        row_h = 50
        
        # Black top bar for hours
        draw.rectangle([(self.margin_x + 150, self.grid_top - 40), (self.margin_x + 150 + self.grid_width, self.grid_top)], fill="black")
        
        # Hour Labels (Midnight, 1, 2... Noon ... Midnight)
        grid_x_start = self.margin_x + 150
        for h in range(25):
            x = grid_x_start + (h * self.hour_width)
            
            # Label text
            label = ""
            if h == 0 or h == 24: label = "Mid-"
            elif h == 12: label = "Noon"
            else: label = str(h % 12) if h % 12 != 0 else "12"
            
            if h < 24: # Don't draw label for end 24 except specifically handled if needed
                draw.text((x + 5, self.grid_top - 35), label, fill="white")
                
            # Vertical Grid Lines
            draw.line([(x, self.grid_top), (x, self.grid_top + (4 * row_h))], fill="gray" if h % 24 != 0 else "black", width=1)
            
            # Tick marks (15, 30, 45)
            if h < 24:
                for q in range(1, 4):
                    qx = x + (q * (self.hour_width / 4))
                    draw.line([(qx, self.grid_top), (qx, self.grid_top + (4 * row_h))], fill="lightgray", width=1)

        # Horizontal Lines & Row Labels
        for i, label in enumerate(labels):
            y = self.grid_top + (i * row_h)
            draw.text((self.margin_x, y + 15), label, fill="black")
            # Top line of row
            draw.line([(grid_x_start, y), (grid_x_start + self.grid_width, y)], fill="black", width=1)
            
        # Bottom line
        draw.line([(grid_x_start, self.grid_top + (4 * row_h)), (grid_x_start + self.grid_width, self.grid_top + (4 * row_h))], fill="black", width=1)
        
        # Total Hours Column
        draw.text((grid_x_start + self.grid_width + 10, self.grid_top - 35), "Total", fill="black")
        draw.text((grid_x_start + self.grid_width + 10, self.grid_top - 20), "Hours", fill="black")
        
        # Draw Totals
        totals = day_info.get('totals', [0,0,0,0]) # Off, SB, D, ON
        for i, total in enumerate(totals):
            y = self.grid_top + (i * row_h) + 15
            draw.text((grid_x_start + self.grid_width + 20, y), f"{total:.2f}", fill="black")

        # --- REMARKS SECTION ---
        rem_y = self.grid_top + 250
        draw.text((self.margin_x, rem_y), "Remarks", fill="black")
        
        # Box for remarks
        draw.line([(self.margin_x, rem_y + 20), (self.width - self.margin_x, rem_y + 20)], fill="black", width=1)
        draw.line([(self.margin_x, rem_y + 20), (self.margin_x, rem_y + 300)], fill="black", width=1)
        draw.line([(self.width - self.margin_x, rem_y + 20), (self.width - self.margin_x, rem_y + 300)], fill="black", width=1)
        draw.line([(self.margin_x, rem_y + 300), (self.width - self.margin_x, rem_y + 300)], fill="black", width=1)

        # Draw actual remark lines
        # events should be passed in day_info or drawn separately. 
        # But create_blank_log is usually called first.
        # Let's trust that draw_events might handle lines?
        # Actually proper standard is that remarks are text list.
        # We can pass them in day_info['remarks_list']
        
        remarks_list = day_info.get('remarks_list', [])
        current_rem_y = rem_y + 30
        for rem in remarks_list:
            # Format: Time - Location - Remark
            # e.g "06:15 - Green Bay, WI - Pre-trip Inspection"
            draw.text((self.margin_x + 10, current_rem_y), rem, fill="black")
            current_rem_y += 20
            if current_rem_y > rem_y + 280:
                break # overflow protection
        
        # --- RECAP SECTION ---
        recap_y = self.height - 150
        draw.text((self.margin_x, recap_y - 25), "Recap: Complete at end of day", fill="black")
        
        # Recap data
        recap = day_info.get('recap', {})
        
        # Table geometry
        table_x = self.margin_x + 200
        table_y = recap_y
        table_w = 1000
        table_h = 100
        
        # Draw Box
        draw.rectangle([(table_x, table_y), (table_x + table_w, table_y + table_h)], outline="black")
        
        # Columns
        # 1. 70/8 Limit (Title)
        # 2. Used last 7
        # 3. Available Today
        # 4. Worked Today
        # 5. Total Since Start
        # 6. Available Tomorrow
        cols = 6
        col_w = table_w / cols
        
        headers = [
            "70 Hr Limit", 
            "Used Last 7 Days", 
            "Avail Today", 
            "Worked Today", 
            "Total 8 Days", 
            "Avail Tomorrow"
        ]
        
        values = [
            recap.get('limit', '70/8'),
            f"{recap.get('used_last_7', 0):.2f}",
            f"{recap.get('available_today', 0):.2f}",
            f"{recap.get('worked_today', 0):.2f}",
            f"{recap.get('total_since_start', 0):.2f}",
            f"{recap.get('available_tomorrow', 0):.2f}"
        ]
        
        # Draw headers and values
        for i in range(cols):
            x = table_x + (i * col_w)
            # Vertical line
            draw.line([(x, table_y), (x, table_y + table_h)], fill="black", width=1)
            
            # Header
            draw.text((x + 5, table_y + 10), headers[i], fill="black")
            
            # Value
            draw.text((x + 20, table_y + 60), values[i], fill="black")  # Larger font ideally, but default ok

        # Horizontal separator
        draw.line([(table_x, table_y + 40), (table_x + table_w, table_y + 40)], fill="black", width=1)

        return img, draw

    def draw_events(self, img, draw, events):
        grid_start_x = self.margin_x + 150
        
        last_x = None
        last_y = None
        
        for event in events:
            row_idx = event['status'] - 1
            # Center of the row
            y_base = self.grid_top + (row_idx * 50) + 25 
            
            start_hour = event['start_hour']
            end_hour = start_hour + event['duration_hours']
            
            x_start = grid_start_x + (start_hour * self.hour_width)
            x_end = grid_start_x + (end_hour * self.hour_width)
            
            # Draw horizontal line
            draw.line([(x_start, y_base), (x_end, y_base)], fill="blue", width=4)
            
            # Connect to previous if exists (Vertical transition line)
            if last_x is not None:
                draw.line([(last_x, last_y), (x_start, y_base)], fill="blue", width=4)
                # Also draw vertical line for the jump itself at the exact time
                # Actually standard HOS charts draw a vertical line AT the time of change
                draw.line([(x_start, last_y), (x_start, y_base)], fill="blue", width=4)
                
            last_x = x_end
            last_y = y_base
            
    def save_image(self, img):
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def save_pdf(self, images):
        if not images:
            return None
        buf = io.BytesIO()
        # Save first image and append the rest
        images[0].save(buf, format='PDF', save_all=True, append_images=images[1:])
        return buf.getvalue()
